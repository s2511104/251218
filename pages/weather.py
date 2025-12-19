import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --------------------------------------------------------------------------------
# 1. 페이지 및 한글 설정
# --------------------------------------------------------------------------------
st.set_page_config(page_title="기온 추세 분석", layout="wide")
st.title("🌡️ 기온 데이터 분석 및 평균 기온 추세선")

# 그래프에서 한글 깨짐 방지를 위해 영어 라벨 사용 (Matplotlib 기본 설정 유지)
# Streamlit 텍스트는 한글로 출력

# --------------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리
# --------------------------------------------------------------------------------
filename = 'ta_20251213130855.csv'

@st.cache_data
def load_and_process_data(file_path):
    # 파일이 존재하는지 확인
    if not os.path.exists(file_path):
        return None, "파일을 찾을 수 없습니다. 같은 폴더에 파일이 있는지 확인해주세요."

    try:
        # csv 파일 읽기 (한글 인코딩 cp949)
        # 데이터 시작 행이 다를 수 있으나, 제공해주신 포맷(헤더 포함)을 기준으로 읽음
        df = pd.read_csv(file_path, encoding='cp949')
        
        # 컬럼명 공백 제거
        df.columns = df.columns.str.strip()
        
        # '날짜' 컬럼 전처리 (특수문자 탭(\t)이나 따옴표 제거)
        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            # datetime으로 변환
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 연도 추출
        df['Year'] = df['날짜'].dt.year
        
        # 필요한 컬럼만 선택 및 숫자형 변환 (오류 발생 시 NaN 처리)
        cols_to_numeric = ['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']
        for col in cols_to_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 데이터가 없는 행 제거
        df = df.dropna(subset=['Year'] + cols_to_numeric)
        df['Year'] = df['Year'].astype(int)

        # ---------------------------------------------------------
        # 일별 데이터를 '연도별' 데이터로 집계 (절대값 구하기 위해)
        # ---------------------------------------------------------
        yearly_df = df.groupby('Year').agg({
            '평균기온(℃)': 'mean',  # 연 평균
            '최저기온(℃)': 'min',   # 그 해의 가장 낮은 기온 (절대 최저)
            '최고기온(℃)': 'max'    # 그 해의 가장 높은 기온 (절대 최고)
        }).reset_index()

        # 컬럼 이름 영문으로 변경 (그래프 깨짐 방지용)
        yearly_df.columns = ['Year', 'Avg_Temp', 'Abs_Min_Temp', 'Abs_Max_Temp']
        
        return yearly_df, None

    except Exception as e:
        return None, f"데이터 처리 중 오류 발생: {e}"

# 데이터 불러오기
df, error_msg = load_and_process_data(filename)

if error_msg:
    st.error(error_msg)
    st.stop() # 에러 발생 시 중단

# --------------------------------------------------------------------------------
# 3. 추세선 계산 (Linear Regression)
# --------------------------------------------------------------------------------
# x: 연도, y: 연평균 기온
x = df['Year']
y = df['Avg_Temp']

# 1차 방정식 (y = ax + b) 계산
# slope(기울기)가 곧 '전년대비 평균기온 상승값'
slope, intercept = np.polyfit(x, y, 1)

# 추세선 함수 (f(x) 만들기)
trend_poly = np.poly1d((slope, intercept))
df['Trend_Line'] = trend_poly(x)

# --------------------------------------------------------------------------------
# 4. 화면 출력 (KPI 및 데이터)
# --------------------------------------------------------------------------------
st.markdown("### 📊 분석 요약")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="분석 기간", value=f"{df['Year'].min()}년 ~ {df['Year'].max()}년")
with col2:
    # 기울기를 통해 상승폭 표시
    st.metric(label="연평균 기온 상승 추세 (기울기)", value=f"{slope:.4f} ℃/년", delta=f"{slope*10:.2f}℃ / 10년")

with st.expander("집계된 연도별 데이터 보기"):
    st.dataframe(df)

# --------------------------------------------------------------------------------
# 5. 그래프 그리기 (Matplotlib)
# --------------------------------------------------------------------------------
st.markdown("### 📈 기온 변화 그래프")

fig, ax = plt.subplots(figsize=(12, 6))

# A. 절대 최저 기온 (파란색 점선)
ax.plot(df['Year'], df['Abs_Min_Temp'], label='Absolute Min (Yearly)', color='blue', linestyle='--', alpha=0.4, linewidth=1)

# B. 절대 최고 기온 (초록색 점선)
ax.plot(df['Year'], df['Abs_Max_Temp'], label='Absolute Max (Yearly)', color='green', linestyle='--', alpha=0.4, linewidth=1)

# C. 평균 기온 (검은색 실선)
ax.plot(df['Year'], df['Avg_Temp'], label='Average Temp', color='black', alpha=0.7, linewidth=1.5)

# D. 추세선 (빨간색 굵은 실선) - 평균 기온 기준
ax.plot(df['Year'], df['Trend_Line'], label=f'Trend Line (Rise: {slope:.3f}/yr)', color='red', linewidth=3)

# 그래프 레이아웃 설정 (영문 라벨 사용)
ax.set_title(f"Temperature Trends ({df['Year'].min()} - {df['Year'].max()})", fontsize=15)
ax.set_xlabel("Year")
ax.set_ylabel("Temperature (C)")
ax.legend(loc='best')
ax.grid(True, linestyle=':', alpha=0.6)

st.pyplot(fig)

st.info("※ 그래프 설명: 파란/초록 점선은 각 연도의 가장 춥고 더웠던 기록이며, 검은 선은 연평균 기온입니다. 빨간 선은 평균 기온의 상승 추세를 나타냅니다.")
