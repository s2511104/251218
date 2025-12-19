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
st.title("🌡️ 지난 110년, 기온은 정말 상승했을까?")
st.markdown("""
이 웹앱은 업로드된 기상 데이터를 분석하여 연도별 평균 기온 변화와 추세선을 보여줍니다.
데이터가 실제로 지구 온난화의 경향을 보여주는지 확인해 보세요.
""")

st.divider()

# 데이터 로드 함수 (캐싱 사용으로 속도 향상)
@st.cache_data
def load_data():
    file_name = 'ta_20251213130855.csv'
    
    try:
        # 공공데이터 포털 등의 CSV는 주로 cp949 인코딩을 사용하나, 오류 시 utf-8 시도
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        # 데이터 전처리: 날짜 컬럼의 특수문자 제거 ("\t1907-10-01" 형태 정리)
        # 업로드된 파일의 형식을 기반으로 정리
        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 필요한 컬럼만 선택 및 결측치 제거
        # 지점, 평균기온(℃), 최저기온(℃), 최고기온(℃)
        df = df.dropna(subset=['날짜', '평균기온(℃)'])
        
        # 연도(Year) 컬럼 추가
        df['연도'] = df['날짜'].dt.year
        return df
        
    except FileNotFoundError:
        st.error(f"'{file_name}' 파일을 찾을 수 없습니다. 같은 폴더에 위치시켜 주세요.")
        return None

# 데이터 분석 및 시각화
df = load_data()

if df is not None:
    # 1. 연도별 평균 기온 계산
    yearly_avg = df.groupby('연도')['평균기온(℃)'].mean()
    
    # 2. 추세선(Trend Line) 계산 (1차 선형 회귀)
    # x: 연도, y: 평균기온
    x = yearly_avg.index
    y = yearly_avg.values
    
    # polyfit으로 기울기(slope)와 절편(intercept) 계산
    slope, intercept = np.polyfit(x, y, 1)
    trend_line = slope * x + intercept
    
    # 3. 데이터 프레임 합치기 (차트용)
    chart_data = pd.DataFrame({
        '연평균 기온': y,
        '추세선 (Trend)': trend_line
    }, index=x)

    # --- 메인 지표 표시 ---
    col1, col2, col3 = st.columns(3)
    
    start_year = x.min()
    end_year = x.max()
    temp_change = trend_line[-1] - trend_line[0] # 추세선 기준 변화량
    
    with col1:
        st.metric("분석 기간", f"{start_year}년 ~ {end_year}년", f"{end_year - start_year}년")
    
    with col2:
        st.metric("추세선 기준 기온 상승", f"{temp_change:.2f} ℃", help="추세선을 기준으로 110년간 상승한 온도의 폭입니다.")
        
    with col3:
        st.metric("연간 상승률", f"{slope:.4f} ℃/년", help="1년마다 평균적으로 오르는 기온입니다.")

    # --- 차트 그리기 ---
    st.subheader("📈 연도별 기온 변화와 추세")
    
    # 스트림릿 내장 라인 차트 사용 (한글 폰트 깨짐 방지 및 인터랙티브 기능)
    st.line_chart(
        chart_data,
        color=["#87CEEB", "#FF4B4B"], # 하늘색(실데이터), 빨간색(추세선)
        y_label="기온 (℃)",
        x_label="연도"
    )

    # --- 데이터 상세 보기 (옵션) ---
    with st.expander("📊 원본 데이터 및 통계 보기"):
        st.write("상위 5개 데이터 미리보기:")
        st.dataframe(df.head())
        
        st.write("연도별 통계:")
        st.dataframe(yearly_avg.describe())

else:
    st.warning("데이터를 불러오지 못했습니다. CSV 파일을 확인해주세요.")
