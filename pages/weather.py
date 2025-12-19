import streamlit as st
import pandas as pd
import numpy as np

# --------------------------------------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------------------------------------
st.set_page_config(page_title="기온 추세 분석", layout="wide")
st.title("🌡️ 기온 데이터 분석 및 평균 기온 추세선")

# --------------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리
# --------------------------------------------------------------------------------
filename = 'pages/ta_20251213130855.csv'

@st.cache_data
def load_and_process_data(file_path):
    try:
        # csv 파일 읽기 (한글 인코딩 cp949)
        # os.path.exists 대신 try-except 구문으로 파일 없음 에러 처리
        df = pd.read_csv(file_path, encoding='cp949')
        
        # 컬럼명 공백 제거
        df.columns = df.columns.str.strip()
        
        # '날짜' 컬럼 전처리
        if '날짜' in df.columns:
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 연도 추출
        df['Year'] = df['날짜'].dt.year
        
        # 숫자형 변환
        cols_to_numeric = ['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']
        for col in cols_to_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 결측치 제거
        df = df.dropna(subset=['Year'] + cols_to_numeric)
        df['Year'] = df['Year'].astype(int)

        # 연도별 집계
        yearly_df = df.groupby('Year').agg({
            '평균기온(℃)': 'mean',
            '최저기온(℃)': 'min', 
            '최고기온(℃)': 'max'
        }).reset_index()

        # 컬럼 이름 영문 변경 (Streamlit 차트 범례용)
        yearly_df.columns = ['Year', 'Avg_Temp', 'Abs_Min_Temp', 'Abs_Max_Temp']
        
        return yearly_df, None

    except FileNotFoundError:
        return None, "파일을 찾을 수 없습니다. 경로를 확인해주세요."
    except Exception as e:
        return None, f"데이터 처리 중 오류 발생: {e}"

# 데이터 불러오기
df, error_msg = load_and_process_data(filename)

if error_msg:
    st.error(error_msg)
    st.stop()

# --------------------------------------------------------------------------------
# 3. 추세선 계산 (Numpy 사용)
# --------------------------------------------------------------------------------
x = df['Year']
y = df['Avg_Temp']

# 1차 방정식 계산
slope, intercept = np.polyfit(x, y, 1)
trend_poly = np.poly1d((slope, intercept))
df['Trend_Line'] = trend_poly(x)

# --------------------------------------------------------------------------------
# 4. 화면 출력 (KPI)
# --------------------------------------------------------------------------------
st.markdown("### 📊 분석 요약")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="분석 기간", value=f"{df['Year'].min()}년 ~ {df['Year'].max()}년")
with col2:
    st.metric(label="연평균 기온 상승 추세 (기울기)", value=f"{slope:.4f} ℃/년", delta=f"{slope*10:.2f}℃ / 10년")

with st.expander("데이터 상세 보기"):
    st.dataframe(df)

# --------------------------------------------------------------------------------
# 5. 그래프 그리기 (Streamlit Native Chart)
# --------------------------------------------------------------------------------
st.markdown("### 📈 기온 변화 그래프")

# 차트를 그리기 위해 'Year'를 인덱스로 설정하고 필요한 컬럼만 선택
chart_data = df.set_index('Year')[['Abs_Min_Temp', 'Abs_Max_Temp', 'Avg_Temp', 'Trend_Line']]

# Streamlit 내장 라인 차트 사용 (Matplotlib 대체)
# 색상은 Streamlit이 자동으로 지정하지만, color 파라미터로 지정 가능
st.line_chart(
    chart_data,
    color=["#0000FF", "#008000", "#000000", "#FF0000"], # 파랑(최저), 초록(최고), 검정(평균), 빨강(추세)
    height=500
)

st.info("※ 차트 범례: Abs_Min(파랑), Abs_Max(초록), Avg(검정), Trend_Line(빨강). 차트 위에 마우스를 올리면 상세 수치를 확인할 수 있습니다.")
