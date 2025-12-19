import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 데이터 로드
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="세계 MBTI 성향 분석",
    page_icon="🧠",
    layout="wide"
)

# 한글 폰트 설정 (스트림릿 클라우드 리눅스 환경 호환성을 위해 영문 라벨 권장하지만, 
# 필요한 경우 폰트 설치가 복잡하므로 그래프 라벨은 영문/코드명으로 유지하고 UI는 한글로 구성합니다)
plt.style.use('seaborn-v0_8-whitegrid')

@st.cache_data
def load_data():
    try:
        # 같은 폴더의 csv 파일 로드
        df = pd.read_csv('pages/mbti_data.csv')
        return df
    except FileNotFoundError:
        st.error("❌ 'mbti_data.csv' 파일을 찾을 수 없습니다. 같은 폴더에 파일을 위치시켜주세요.")
        return None

df = load_data()

if df is not None:
    # -------------------------------------------------------------------------
    # 2. 메인 헤더
    # -------------------------------------------------------------------------
    st.title("🌏 국가별 MBTI 성향 분석 대시보드")
    st.markdown("""
    이 대시보드는 전 세계 국가들의 MBTI 성향 데이터를 분석합니다.
    * **전체 국가 평균**: 전 세계적으로 어떤 유형이 가장 흔한지 확인합니다.
    * **국가별 상세**: 특정 국가의 MBTI 분포를 확인합니다.
    * **순위 & 한국 비교**: 특정 MBTI 유형이 가장 많은 나라와 한국의 순위를 비교합니다.
    """)
    st.divider()

    # 데이터의 숫자 컬럼만 추출 (국가명 제외)
    mbti_cols = df.columns[1:] # 첫번째 컬럼이 Country라고 가정
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 전체 국가 평균", "🔍 국가별 상세 분석", "🏆 Top 10 & 한국 비교"])

    # -------------------------------------------------------------------------
    # Tab 1: 전체 국가 평균 비율
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("전 세계 MBTI 유형 평균 비율")
        
        # 각 MBTI 유형별 평균 계산
        global_avg = df[mbti_cols].mean().sort_values(ascending=False)
        
        # 시각화
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=global_avg.index, y=global_avg.values, palette="viridis", ax=ax)
        
        ax.set_ylabel("평균 비율 (Average Ratio)")
        ax.set_xlabel("MBTI Type")
        ax.set_title("Global Average Ratio by MBTI Type")
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        
        with st.expander("데이터 자세히 보기"):
            st.dataframe(global_avg.to_frame(name="Global Average Ratio").T)

    # -------------------------------------------------------------------------
    # Tab 2: 국가별 상세 분석
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("국가별 MBTI 성향 상세")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # 국가 선택 (한국을 기본값으로 찾기 위해 노력)
            country_list = df['Country'].unique().tolist()
            default_ix = 0
            if "South Korea" in country_list:
                default_ix = country_list.index("South Korea")
            elif "Korea, South" in country_list:
                default_ix = country_list.index("Korea, South")
                
            selected_country = st.selectbox("분석할 국가를 선택하세요:", country_list, index=default_ix)
        
        with col2:
            # 선택된 국가 데이터 추출
            country_data = df[df['Country'] == selected_country][mbti_cols].T
            country_data.columns = ['Ratio']
            country_data = country_data.sort_values(by='Ratio', ascending=False)
            
            # 시각화
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            sns.barplot(x=country_data.index, y=country_data['Ratio'], palette="magma", ax=ax2)
            
            ax2.set_title(f"MBTI Distribution in {selected_country}")
            ax2.set_ylabel("비율 (Ratio)")
            plt.xticks(rotation=45)
            
            st.pyplot(fig2)
            st.info(f"💡 **{selected_country}**에서 가장 높은 비중을 차지하는 유형은 **{country_data.index[0]}** 입니다.")

    # -------------------------------------------------------------------------
    # Tab 3: MBTI 유형별 Top 10 & 한국 비교
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("MBTI 유형별 Top 10 국가 및 한국 비교")
        
        target_mbti = st.selectbox("순위를 확인하고 싶은 MBTI 유형을 선택하세요:", mbti_cols)
        
        # 해당 MBTI 기준으로 정렬하여 Top 10 추출
        top_10 = df[['Country', target_mbti]].sort_values(by=target_mbti, ascending=False).head(10)
        
        # 한국 데이터 찾기
        korea_row = df[df['Country'].isin(['South Korea', 'Korea, South'])]
        
        col_l, col_r = st.columns([2, 1])
        
        with col_l:
            # Top 10 시각화
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            
            # 기본 색상 설정
            colors = ['lightgray'] * len(top_10)
            
            # 만약 Top 10 안에 한국이 있다면 색상 강조
            for i, country in enumerate(top_10['Country']):
                if country in ['South Korea', 'Korea, South']:
                    colors[i] = 'crimson'  # 한국 강조색
                else:
                    colors[i] = 'steelblue'

            sns.barplot(x='Country', y=target_mbti, data=top_10, palette=colors, ax=ax3)
            ax3.set_title(f"Top 10 Countries for {target_mbti}")
            ax3.set_ylabel("비율 (Ratio)")
            plt.xticks(rotation=45)
            st.pyplot(fig3)

        with col_r:
            st.markdown(f"### 🇰🇷 한국 데이터 비교")
            
            if not korea_row.empty:
                korea_val = korea_row[target_mbti].values[0]
                korea_rank = df[target_mbti].rank(ascending=False).loc[korea_row.index[0]]
                korea_name = korea_row['Country'].values[0]
                
                st.metric(label=f"{korea_name}의 {target_mbti} 비율", value=f"{korea_val:.4f}")
                st.metric(label="세계 순위", value=f"{int(korea_rank)}위 / {len(df)}개국")
                
                # Top 10에 들었는지 확인 메시지
                if int(korea_rank) <= 10:
                    st.success(f"🎉 한국은 **{target_mbti}** 유형 비율이 세계 **Top 10**에 포함됩니다!")
                else:
                    st.info(f"한국은 Top 10에 들지 않았지만, 전체 {len(df)}개국 중 상위 **{int(korea_rank)}위**입니다.")
            else:
                st.warning("데이터셋에서 'South Korea' 또는 'Korea, South'를 찾을 수 없습니다.")

        st.caption("데이터 출처: 업로드된 mbti_data.csv")

else:
    st.stop()
