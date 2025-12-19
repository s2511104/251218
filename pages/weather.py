import streamlit as st
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="110년 기온 종합 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 기온 변화 종합 대시보드")
st.markdown("""
**절대 최저/최고기온**과 **평균기온**을 동시에 분석합니다.
전체적인 기온 상승 경향을 파악하기 위해 **평균기온에만 추세선(빨간색)**을 적용했습니다.
""")
st.divider()

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    file_name = 'pages/ta_20251213130855.csv'
    
    try:
        # 파일 읽기 및 인코딩 처리
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        # 날짜 컬럼 정리 (특수문자 제거)
        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 기온 데이터 숫자 변환 (오류 데이터 NaN 처리)
        cols = ['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 결측치 제거
        df = df.dropna(subset=['날짜'] + cols)
        df['연도'] = df['날짜'].dt.year
        
        return df
        
    except FileNotFoundError:
        return None

df = load_data()

if df is not None:
    # 1. 데이터 집계 (평균은 mean, 극값은 min/max)
    yearly_df = df.groupby('연도').agg({
        '최저기온(℃)': 'min',   # 그 해 가장 추운 날
        '평균기온(℃)': 'mean',  # 그 해 평균 기온
        '최고기온(℃)': 'max'    # 그 해 가장 더운 날
    })
    
    # 2. 추세선 계산 (평균기온에 대해서만 수행)
    x = yearly_df.index.values # 연도
    y = yearly_df['평균기온(℃)'].values
    
    slope, intercept = np.polyfit(x, y, 1) # 1차 방정식 계산
    trend_line = slope * x + intercept
    
    # 3. 차트용 데이터프레임 생성
    # 컬럼 순서가 그래프 색상 매핑 순서가 됩니다.
    chart_df = pd.DataFrame({
        '최저기온(절대값)': yearly_df['최저기온(℃)'],
        '평균기온': yearly_df['평균기온(℃)'],
        '최고기온(절대값)': yearly_df['최고기온(℃)'],
        '🔴 평균기온 추세선': trend_line
    }, index=yearly_df.index)
    
    # 연도 쉼표 제거 (문자열 변환)
    chart_df.index = chart_df.index.map(str)

    # --- 상단 지표 ---
    st.subheader("📊 데이터 요약")
    col1, col2, col3 = st.columns(3)
    
    total_change = trend_line[-1] - trend_line[0]
    
    with col1:
        st.metric("평균기온 상승폭 (추세선 기준)", f"{total_change:+.2f}℃")
    with col2:
        st.metric("역대 최저 기온", f"{yearly_df['최저기온(℃)'].min()}℃")
    with col3:
        st.metric("역대 최고 기온", f"{yearly_df['최고기온(℃)'].max()}℃")

    st.divider()

    # --- 메인 그래프 ---
    st.subheader("📈 연도별 기온 변화와 추세")
    st.markdown("가운데 **초록색 실선(평균기온)**을 가로지르는 **빨간색 직선**이 기온 상승 추세입니다.")
    
    # 색상 지정 순서:
    # 1. 최저기온 -> 파랑 (#1E90FF)
    # 2. 평균기온 -> 초록 (#2E8B57)
    # 3. 최고기온 -> 주황 (#FFA500)
    # 4. 추세선 -> 빨강 (#FF0000)
    st.line_chart(
        chart_df,
        color=["#1E90FF", "#2E8B57", "#FFA500", "#FF0000"],
        height=500
    )
    
    with st.expander("데이터 자세히 보기"):
        st.dataframe(yearly_df.style.format("{:.1f}"))

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
