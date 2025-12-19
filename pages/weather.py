import streamlit as st
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="110년 기온 극값과 추세 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 한파와 폭염, 110년간 어떻게 변했을까?")
st.markdown("""
연도별 **가장 추웠던 날(절대 최저)**과 **가장 더웠던 날(절대 최고)**의 기온을 분석합니다.
**빨간색 직선(추세선)**을 통해 불규칙한 날씨 속에서도 뚜렷한 **상승 경향**이 있는지 확인해보세요.
""")
st.divider()

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_and_clean_data():
    file_name = 'pages/ta_20251213130855.csv'
    
    try:
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        target_cols = ['최저기온(℃)', '최고기온(℃)']
        for col in target_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=['날짜'] + target_cols)
        df['연도'] = df['날짜'].dt.year
        
        return df
        
    except FileNotFoundError:
        return None

# 추세선 계산 함수 (1차 함수 y = ax + b)
def get_trend_line(x_data, y_data):
    slope, intercept = np.polyfit(x_data, y_data, 1)
    return slope * x_data + intercept, slope, intercept

# 메인 로직
df = load_and_clean_data()

if df is not None:
    # 1. 연도별 극값(Extreme) 추출 (min, max)
    yearly_df = df.groupby('연도').agg({
        '최저기온(℃)': 'min',
        '최고기온(℃)': 'max'
    })
    
    # 2. 추세선 데이터 생성
    years = yearly_df.index.values
    
    # 최저기온 추세선 계산
    min_trend, min_slope, min_intercept = get_trend_line(years, yearly_df['최저기온(℃)'])
    
    # 최고기온 추세선 계산
    max_trend, max_slope, max_intercept = get_trend_line(years, yearly_df['최고기온(℃)'])
    
    # 3. 차트용 데이터프레임 합치기
    # 순서: [최저실제, 최저추세, 최고실제, 최고추세] -> 색상 매핑을 위해 순서 중요
    chart_df = pd.DataFrame({
        '연도': years,
        '최저기온(실제)': yearly_df['최저기온(℃)'],
        '📉 최저 추세선': min_trend,
        '최고기온(실제)': yearly_df['최고기온(℃)'],
        '📈 최고 추세선': max_trend
    })
    
    # 연도를 인덱스로 설정하고 문자열로 변환 (2,025 콤마 제거)
    chart_df.set_index('연도', inplace=True)
    chart_df.index = chart_df.index.map(str)

    # --- 상단 지표 (Metrics) ---
    st.subheader("📊 110년간의 변화 요약")
    col1, col2 = st.columns(2)
    
    # 전체 기간 상승폭 계산 (추세선 기준 끝값 - 시작값)
    total_min_change = min_trend[-1] - min_trend[0]
    total_max_change = max_trend[-1] - max_trend[0]

    with col1:
        st.metric("한파(최저기온) 약화", f"{total_min_change:+.1f}℃", f"{min_slope:+.4f}℃/년")
        st.info("겨울철 극한 추위가 예전보다 훨씬 따뜻해졌음을 의미합니다.")
        
    with col2:
        st.metric("폭염(최고기온) 강화", f"{total_max_change:+.1f}℃", f"{max_slope:+.4f}℃/년")
        st.error("여름철 극한 더위가 예전보다 더 심해졌음을 의미합니다.")

    st.divider()

    # --- 그래프 그리기 ---
    st.subheader("📈 연도별 극값과 추세선 (Trend Line)")
    st.markdown("얇은 선은 실제 매년 기록이며, **굵은 빨간 계열 선이 추세선**입니다.")
    
    # 색상 지정 (컬럼 순서대로):
    # 1. 최저기온(실제) -> 파랑 (#1E90FF)
    # 2. 최저기온(추세) -> 진한 빨강 (#B22222)
    # 3. 최고기온(실제) -> 주황 (#FFA500)
    # 4. 최고기온(추세) -> 밝은 빨강 (#FF0000)
    st.line_chart(
        chart_df,
        color=['#1E90FF', '#B22222', '#FFA500', '#FF0000'], 
        height=500
    )
    
    # --- 데이터 표 ---
    with st.expander("📄 데이터 상세 보기"):
        st.dataframe(chart_df.style.format("{:.1f}"), use_container_width=True)

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
