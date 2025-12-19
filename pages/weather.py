import streamlit as st
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="110년 기온 변화 정밀 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 지난 110년, 기온은 실제로 얼마나 올랐을까?")
st.markdown("""
업로드된 기상 데이터를 기반으로 **평균기온, 최저기온, 최고기온**의 변화를 정밀 분석합니다.
데이터의 오염(특수문자 등)을 제거하고 순수 숫자 데이터만 추출하여 분석했습니다.
""")
st.divider()

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_and_clean_data():
    file_name = 'ta_20251213130855.csv'
    
    try:
        # 1. 파일 읽기 (인코딩 처리)
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        # 2. 날짜 컬럼 전처리 (탭, 따옴표 제거)
        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 3. 데이터 강제 숫자 변환
        target_cols = ['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']
        for col in target_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 4. 결측치(NaN) 제거
        df = df.dropna(subset=['날짜'] + target_cols)
        
        # 5. 연도 추출
        df['연도'] = df['날짜'].dt.year
        
        return df, target_cols

    except FileNotFoundError:
        return None, []

# 데이터 불러오기
df, cols = load_and_clean_data()

if df is not None:
    # --- 데이터 집계 (연도별 평균) ---
    yearly_df = df.groupby('연도')[cols].mean()
    
    start_year = yearly_df.index.min()
    end_year = yearly_df.index.max()

    # --- 1. 종합 요약 지표 (Metrics) ---
    st.subheader(f"📊 분석 결과 요약 ({start_year}년 ~ {end_year}년)")
    
    col1, col2, col3 = st.columns(3)
    
    # 각 지표별 상승폭 계산 함수
    def calculate_trend(y_values):
        x = np.arange(len(y_values))
        slope, intercept = np.polyfit(x, y_values, 1)
        change = (slope * x[-1] + intercept) - (slope * x[0] + intercept)
        return change, slope

    # 평균기온
    mean_change, mean_slope = calculate_trend(yearly_df['평균기온(℃)'])
    with col1:
        st.metric("평균기온 상승", f"{mean_change:+.2f}℃", f"{mean_slope:+.4f}℃/년")
        st.caption("지난 110년간 평균적인 기온 상승폭")

    # 최저기온
    min_change, min_slope = calculate_trend(yearly_df['최저기온(℃)'])
    with col2:
        st.metric("최저기온 상승", f"{min_change:+.2f}℃", f"{min_slope:+.4f}℃/년")
        st.caption("아침 최저 기온 상승폭")

    # 최고기온
    max_change, max_slope = calculate_trend(yearly_df['최고기온(℃)'])
    with col3:
