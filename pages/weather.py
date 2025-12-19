import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="기온 데이터 정밀 분석", page_icon="🌡️", layout="wide")

st.title("🌡️ 기온 데이터 정밀 검증")
st.markdown("데이터가 오염되지 않았는지 숫자로 강제 변환하여 다시 분석합니다.")
st.divider()

@st.cache_data
def load_data():
    file_name = 'ta_20251213130855.csv'
    
    try:
        try:
            df = pd.read_csv(file_name, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, encoding='utf-8')

        # 1. 날짜 컬럼 전처리 (이전과 동일)
        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')

        # 2. ★ 핵심 수정: 기온 데이터 강제 숫자 변환 ★
        # 숫자가 아닌 값(특수문자 등)이 섞여 있으면 NaN(결측치)으로 바꿔버리고 제거합니다.
        # 이렇게 해야 그래프가 겹치거나 이상하게 나오는 현상을 막습니다.
        cols = ['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 날짜나 기온이 하나라도 없는 행은 삭제
        df = df.dropna(subset=['날짜'] + cols)
        
        df['연도'] = df['날짜'].dt.year
        return df
        
    except FileNotFoundError:
        st.error(f"'{file_name}' 파일을 찾을 수 없습니다.")
        return None

df = load_data()

if df is not None:
    # 데이터가 제대로 숫자로 읽혔는지 눈으로 확인시켜주는 구간
    st.subheader("1. 데이터 검증 (상위 5개 행)")
    st.markdown("아래 표의 숫자가 정상적으로 보이고, 서로 다른 값인지 확인해보세요.")
    st.dataframe(df.head())

    # --- 그래프 그리기 ---
    st.subheader("2. 연도별 기온 추세 비교")
    
    # 연도별 평균 구하기
    yearly_data = df.groupby('연도')[['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']].mean()
    
    # 차트용 데이터 가공 (연도 쉼표 제거)
    chart_df = yearly_data.reset_index()
    chart_df['연도'] = chart_df['연도'].astype(str)
    
    # 그래프 그리기
    st.line_chart(
        chart_df.set_index('연도'),
        color=["#2E8B57", "#1E90FF", "#FF4500"], # 평균(초록), 최저(파랑), 최고(주황)
        height=500
    )

    # --- 통계 수치 확인 ---
    st.subheader("3. 실제 통계 차이 확인")
    col1, col2 = st.columns(2)
    
    # 최고기온 평균과 최저기온 평균의 전체 차이를 계산
    avg_max = df['최고기온(℃)'].mean()
    avg_min = df['최저기온(℃)'].mean()
    
    with col1:
        st.metric("전체 기간 평균 최고기온", f"{avg_max:.1f} ℃")
    with col2:
        st.metric("전체 기간 평균 최저기온", f"{avg_min:.1f} ℃")
        
    st.info(f"💡 두 값의 차이는 평균적으로 약 {avg_max - avg_min:.1f}℃ 입니다. 그래프에서 이 간격이 유지되어야 정상입니다.")

else:
    st.warning("데이터를 불러올 수 없습니다.")
