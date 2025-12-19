import streamlit as st
import pandas as pd
import numpy as np

# 페이지 기본 설정
st.set_page_config(
    page_title="110년간의 기온 변화 분석",
    page_icon="🌡️",
    layout="wide"
)

# 제목 및 설명
st.title("🌡️ 지난 110년, 대한민국 기온은 상승했을까?")
st.markdown("""
업로드된 기상 데이터를 분석하여 연도별 **평균기온, 최고기온, 최저기온**의 변화 추세를 확인합니다.
데이터에 포함된 노이즈를 제거하고 연평균 값을 산출하여 분석했습니다.
""")
st.divider()

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    file_name = 'pages/ta_20251213130855.csv'
    
    try:
        # 1. 파일 읽기 (CP949 인코딩 시도 후 UTF-8 시도)
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        # 2. 날짜 컬럼 전처리 (데이터에 포함된 탭(\t)과 따옴표(") 제거)
        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 3. 숫자 데이터 강제 변환 (오류 발생 시 NaN 처리)
        cols = ['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 4. 결측치 제거 및 연도 추출
        df = df.dropna(subset=['날짜'] + cols)
        df['연도'] = df['날짜'].dt.year
        
        return df, cols

    except FileNotFoundError:
        st.error(f"'{file_name}' 파일을 찾을 수 없습니다. 같은 폴더에 위치시켜 주세요.")
        return None, []

# 데이터 불러오기
df, target_cols = load_data()

if df is not None:
    # 연도별 평균 계산
    yearly_df = df.groupby('연도')[target_cols].mean()
    
    # 분석 기간
    start_year = yearly_df.index.min()
    end_year = yearly_df.index.max()
    
    # --- 상단 지표 (Metrics) ---
    st.subheader(f"📊 기온 상승 분석 결과 ({start_year} ~ {end_year})")
    
    col1, col2, col3 = st.columns(3)
    
    # 추세선 및 상승폭 계산 함수
    def get_trend(series):
        x = series.index.values
        y = series.values
        slope, intercept = np.polyfit(x, y, 1) # 1차 선형 회귀
        total_change = (slope * x[-1] + intercept) - (slope * x[0] + intercept)
        return total_change, slope

    # 1. 평균기온 변화
    avg_change, avg_slope = get_trend(yearly_df['평균기온(℃)'])
    with col1:
        st.metric(
            label="평균기온 상승폭",
            value=f"{avg_change:+.2f}℃",
            delta=f"{avg_slope:+.4f}℃/년"
        )
        
    # 2. 최저기온 변화
    min_change, min_slope = get_trend(yearly_df['최저기온(℃)'])
    with col2:
        st.metric(
            label="최저기온 상승폭",
            value=f"{min_change:+.2f}℃",
            delta=f"{min_slope:+.4f}℃/년"
        )
        
    # 3. 최고기온 변화
    max_change, max_slope = get_trend(yearly_df['최고기온(℃)'])
    with col3:
        st.metric(
            label="최고기온 상승폭",
            value=f"{max_change:+.2f}℃",
            delta=f"{max_slope:+.4f}℃/년"
        )

    st.caption("※ '상승폭'은 추세선을 기준으로 계산된 110년간의 총 변화량이며, 작은 글씨는 연간 변화율입니다.")
    st.divider()

    # --- 메인 차트 ---
    st.subheader("📈 연도별 기온 변화 그래프")
    
    # 차트용 데이터 (연도를 문자열로 변환하여 2,025 같은 쉼표 표기 방지)
    chart_data = yearly_df.copy()
    chart_data.index = chart_data.index.astype(str)
    
    # 라인 차트 그리기
    st.line_chart(
        chart_data,
        color=["#2E8B57", "#1E90FF", "#FF4500"], # 초록(평균), 파랑(최저), 주황(최고)
        height=500
    )

    # --- 데이터 상세 보기 ---
    with st.expander("🔎 데이터 상세 보기"):
        st.write("연도별 평균 데이터:")
        st.dataframe(yearly_df.style.format("{:.2f}"))

else:
    st.warning("데이터를 불러오지 못했습니다.")
