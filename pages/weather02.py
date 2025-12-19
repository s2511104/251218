import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --------------------------------------------------------------------------------
# 1. 페이지 기본 설정
# --------------------------------------------------------------------------------
st.set_page_config(page_title="기후 변화 분석", page_icon="🌡️", layout="wide")

st.title("🌡️ 지난 110년간 기온 상승 추세 분석")
st.markdown("""
이 대시보드는 1907년부터 현재까지의 기온 데이터를 분석하여 
**실제로 지구 온난화가 진행되고 있는지** 시각적으로 확인하기 위해 제작되었습니다.
""")

# --------------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리 함수
# --------------------------------------------------------------------------------
@st.cache_data
def load_data(file_path):
    # 인코딩 문제 해결을 위한 순차적 시도
    encodings = ['utf-8', 'cp949', 'euc-kr']
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            return None
            
    if df is None:
        return None

    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 데이터 전처리: '날짜' 컬럼 정제 (특수문자 제거)
    if '날짜' in df.columns:
        # 데이터에 포함된 탭(\t)이나 따옴표(") 제거
        df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 연도 추출
    df['Year'] = df['날짜'].dt.year
    
    # 숫자 데이터 변환 (에러 발생 시 NaN 처리)
    cols = ['평균기온(℃)', '최저기온(℃)', '최고기온(℃)']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 연도별 평균 데이터 집계 (노이즈를 줄이고 추세를 보기 위함)
    df_yearly = df.groupby('Year')[cols].mean().reset_index()
    
    # 컬럼명 영문 변환 (Plotly 등에서 다루기 쉽게)
    df_yearly.columns = ['Year', 'Avg_Temp', 'Min_Temp', 'Max_Temp']
    
    return df_yearly

# --------------------------------------------------------------------------------
# 3. 데이터 불러오기 및 추세선 계산
# --------------------------------------------------------------------------------
filename = 'pages/ta_20251213130855.csv'
df = load_data(filename)

if df is None:
    st.error(f"❌ '{filename}' 파일을 찾을 수 없습니다. 같은 폴더에 파일이 있는지 확인해주세요.")
    st.stop()

# 추세선(Trend Line) 계산 - 1차 방정식 (y = ax + b)
# x: 연도, y: 평균기온
x = df['Year']
y = df['Avg_Temp']

# 결측치가 있으면 계산이 안되므로 제거
valid_idx = np.isfinite(x) & np.isfinite(y)
slope, intercept = np.polyfit(x[valid_idx], y[valid_idx], 1)

# 추세선 값 생성
df['Trend'] = slope * df['Year'] + intercept

# 상승폭 계산
start_temp = df['Trend'].iloc[0]
end_temp = df['Trend'].iloc[-1]
total_change = end_temp - start_temp

# --------------------------------------------------------------------------------
# 4. 분석 결과 요약 (KPI)
# --------------------------------------------------------------------------------
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("분석 기간", f"{df['Year'].min()}년 ~ {df['Year'].max()}년", f"{len(df)}년 데이터")

with col2:
    # 100년 환산 상승폭
    century_change = slope * 100
    st.metric("100년당 기온 상승률", f"{century_change:.2f} ℃", "매우 빠름" if century_change > 1.0 else "보통")

with col3:
    st.metric("총 기온 상승 (추세선 기준)", f"{total_change:.2f} ℃", delta="상승 중" if slope > 0 else "하강 중")

# --------------------------------------------------------------------------------
# 5. Plotly 인터랙티브 그래프 시각화
# --------------------------------------------------------------------------------
st.subheader("📈 연도별 평균 기온과 온난화 추세선")

# 그래프 생성
fig = go.Figure()

# A. 실제 관측 데이터 (연평균 기온) - 산점도+라인
fig.add_trace(go.Scatter(
    x=df['Year'], 
    y=df['Avg_Temp'],
    mode='markers+lines',
    name='연평균 기온 (Actual)',
    marker=dict(size=6, color='royalblue', opacity=0.5),
    line=dict(width=1, color='royalblue'),
    hovertemplate='%{x}년: %{y:.1f}℃'
))

# B. 추세선 (Linear Regression)
fig.add_trace(go.Scatter(
    x=df['Year'], 
    y=df['Trend'],
    mode='lines',
    name='기온 상승 추세 (Trend)',
    line=dict(color='red', width=4),
    hovertemplate='%{x}년 추세: %{y:.1f}℃'
))

# 그래프 레이아웃 설정
fig.update_layout(
    title=dict(text='관측 이래 기온 변화 양상', font=dict(size=20)),
    xaxis_title='연도 (Year)',
    yaxis_title='평균 기온 (℃)',
    hovermode="x unified", # 마우스 오버 시 x축 기준 모든 데이터 표시
    template='plotly_white', # 깔끔한 흰색 배경
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

# y축 범위 자동 조정 (여유 공간 확보)
y_min = df['Avg_Temp'].min() - 1
y_max = df['Avg_Temp'].max() + 1
fig.update_yaxes(range=[y_min, y_max])

# Streamlit에 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------------
# 6. 데이터 탐색기
# --------------------------------------------------------------------------------
with st.expander("🔍 원본 데이터 확인하기"):
    st.dataframe(df.sort_values(by='Year', ascending=False), use_container_width=True)
