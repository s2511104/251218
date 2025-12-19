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

# 데이터 로드 함수
@st.cache_data
def load_data():
    # 깃허브에 올린 파일명과 정확히 일치해야 합니다.
    file_name = 'pages/ta_20251213130855.csv'
    
    try:
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        df = df.dropna(subset=['날짜', '평균기온(℃)'])
        df['연도'] = df['날짜'].dt.year
        return df
        
    except FileNotFoundError:
        st.error(f"'{file_name}' 파일을 찾을 수 없습니다.")
        return None

# 데이터 분석 및 시각화
df = load_data()

if df is not None:
    # 1. 데이터 가공
    yearly_avg = df.groupby('연도')['평균기온(℃)'].mean()
    x = yearly_avg.index
    y = yearly_avg.values
    
    # 추세선 계산
    slope, intercept = np.polyfit(x, y, 1)
    trend_line = slope * x + intercept
    
    # 2. 차트용 데이터 만들기 (핵심 수정 부분!)
    chart_df = pd.DataFrame({
        '연도': x,
        '실제 기온': y,
        '추세선': trend_line
    })
    
    # ★ 핵심 트릭: 연도를 숫자가 아닌 '문자열'로 변환
    # 이렇게 하면 그래프가 2,015로 표시하지 않고 "2015"라는 글자로 인식합니다.
    chart_df['연도'] = chart_df['연도'].astype(str)

    # 3. 메인 지표 표시
    col1, col2, col3 = st.columns(3)
    
    # 지표 계산용 (숫자형 연도 사용)
    start_year = x.min()
    end_year = x.max()
    temp_change = trend_line[-1] - trend_line[0]
    
    with col1:
        st.metric("분석 기간", f"{start_year}년 ~ {end_year}년", f"{end_year - start_year}년")
    with col2:
        st.metric("추세선 기준 기온 상승", f"{temp_change:.2f} ℃")
    with col3:
        st.metric("연간 상승률", f"{slope:.4f} ℃/년")

    # 4. 차트 그리기 (기본 st.line_chart 사용)
    st.subheader("📈 연도별 기온 변화와 추세")
    
    # 연도를 인덱스로 설정하여 그리기
    st.line_chart(
        chart_df.set_index('연도'),
        color=["#87CEEB", "#FF4B4B"], # 하늘색, 빨간색
        height=400
    )

    # 5. 데이터 표 보기
    with st.expander("📊 원본 데이터 및 통계 보기"):
        st.write("연도별 평균 기온 데이터:")
        
        # 표에서도 쉼표를 빼기 위해 column_config 사용 (스트림릿 내장 기능)
        st.dataframe(
            chart_df,
            column_config={
                "연도": st.column_config.TextColumn("연도"), # 문자로 취급
                "실제 기온": st.column_config.NumberColumn(format="%.2f ℃"),
                "추세선": st.column_config.NumberColumn(format="%.2f ℃"),
            },
            hide_index=True,
            use_container_width=True
        )

else:
    st.warning("데이터를 불러오지 못했습니다.")
