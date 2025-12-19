import streamlit as st
import pandas as pd
import numpy as np

# 페이지 기본 설정
st.set_page_config(
    page_title="110년간의 기온 변화 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 지난 110년, 기온은 정말 상승했을까?")
st.markdown("데이터 출처: 기상청 (업로드된 파일 기반)")
st.divider()

# 데이터 로드 함수
@st.cache_data
def load_data():
    file_name = 'pages/ta_20251213130855.csv'
    
    try:
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 필요한 컬럼만 선택 (최고, 최저 기온 추가)
        df = df.dropna(subset=['날짜', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)'])
        df['연도'] = df['날짜'].dt.year
        return df
        
    except FileNotFoundError:
        st.error(f"'{file_name}' 파일을 찾을 수 없습니다.")
        return None

df = load_data()

if df is not None:
    # --- 1. 분석할 데이터 선택 (라디오 버튼) ---
    st.subheader("🔍 온도별 상세 분석")
    
    option = st.radio(
        "어떤 기준의 기온 변화를 보시겠습니까?",
        ('평균기온(℃)', '최고기온(℃)', '최저기온(℃)'),
        horizontal=True
    )
    
    # 선택된 컬럼으로 연도별 평균 계산
    yearly_data = df.groupby('연도')[option].mean()
    x = yearly_data.index
    y = yearly_data.values
    
    # 추세선 계산
    slope, intercept = np.polyfit(x, y, 1)
    trend_line = slope * x + intercept
    
    # 차트용 데이터 (선택된 옵션 + 추세선)
    chart_df = pd.DataFrame({
        '연도': x,
        '실제 기록': y,
        '추세선': trend_line
    })
    chart_df['연도'] = chart_df['연도'].astype(str) # 쉼표 제거용 문자열 변환

    # 지표 표시
    col1, col2, col3 = st.columns(3)
    temp_change = trend_line[-1] - trend_line[0]
    
    with col1:
        st.metric(f"선택: {option}", f"{x.min()}년 ~ {x.max()}년")
    with col2:
        st.metric("110년간 상승폭", f"{temp_change:.2f} ℃")
    with col3:
        st.metric("연간 상승률", f"{slope:.4f} ℃/년")

    # 선택된 데이터 차트 그리기
    st.line_chart(
        chart_df.set_index('연도'),
        color=["#87CEEB", "#FF4B4B"],
        height=350
    )
    
    st.divider()

    # --- 2. 종합 비교 그래프 (평균/최고/최저 한꺼번에) ---
    st.subheader("📊 전체 기온 비교 (평균 vs 최고 vs 최저)")
    st.markdown("모든 기온 데이터를 한 번에 겹쳐서 비교합니다.")

    # 전체 데이터 연도별 집계
    all_years = df.groupby('연도')[['평균기온(℃)', '최고기온(℃)', '최저기온(℃)']].mean()
    
    # 인덱스(연도)를 컬럼으로 빼고 문자열로 변환 (쉼표 제거)
    all_chart_df = all_years.reset_index()
    all_chart_df['연도'] = all_chart_df['연도'].astype(str)
    
    # 3개 라인 동시에 그리기
    st.line_chart(
        all_chart_df.set_index('연도'),
        color=["#2E8B57", "#FF4500", "#1E90FF"], # 초록(평균), 주황(최고), 파랑(최저)
        height=500
    )

    # 데이터 표 보여주기
    with st.expander("📄 전체 데이터 표로 보기"):
        st.dataframe(
            all_chart_df,
            column_config={
                "연도": st.column_config.TextColumn("연도"),
                "평균기온(℃)": st.column_config.NumberColumn(format="%.1f ℃"),
                "최고기온(℃)": st.column_config.NumberColumn(format="%.1f ℃"),
                "최저기온(℃)": st.column_config.NumberColumn(format="%.1f ℃"),
            },
            hide_index=True,
            use_container_width=True
        )

else:
    st.warning("데이터를 불러오지 못했습니다.")
