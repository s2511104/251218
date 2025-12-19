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

# 그래프 스타일 설정
plt.style.use('seaborn-v0_8-whitegrid')

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('pages/mbti_data.csv')
        return df
    except FileNotFoundError:
        st.error("❌ 'mbti_data.csv' 파일을 찾을 수 없습니다. 같은 폴더에 파일을 위치시켜주세요.")
        return None

# -----------------------------------------------------------------------------
# 원그래프 그리기 도우미 함수 (Top 8 + Others)
# -----------------------------------------------------------------------------
def plot_pie_chart(data_series, title, ax):
    """
    상위 8개만 표시하고 나머지는 'Others'로 묶어 원그래프를 그립니다.
    """
    data_sorted = data_series.sort_values(ascending=False)
    
    # 상위 8개 추출
    top_n = 8
    if len(data_sorted) > top_n:
        top_slice = data_sorted[:top_n]
        others_value = data_sorted[top_n:].sum()
        top_slice['Others'] = others_value
    else:
        top_slice = data_sorted

    # 원그래프 그리기
    wedges, texts, autotexts = ax.pie(
        top_slice, 
        labels=top_slice.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=sns.color_palette("pastel"),
        wedgeprops={'edgecolor': 'white'}
    )
    
    ax.set_title(title, pad=20)
    plt.setp(texts, size=10)
    plt.setp(autotexts, size=10, weight="bold")

# -----------------------------------------------------------------------------
# 메인 로직
# -----------------------------------------------------------------------------
df = load_data()

if df is not None:
    st.title("🌏 국가별 MBTI 성향 분석 대시보드")
    st.markdown("""
    * **전체 국가 평균**: 전 세계 MBTI 평균 비율
    * **국가별 상세**: 특정 국가의 분포 확인
    * **순위 비교**: 특정 MBTI 유형의 국가별 순위
    """)
    st.divider()

    mbti_cols = df.columns[1:] 
    
    tab1, tab2, tab3 = st.tabs(["📊 전체 국가 평균", "🔍 국가별 상세 분석", "🏆 Top 10 & 한국 비교"])

    # -------------------------------------------------------------------------
    # Tab 1: 전체 국가 평균 (세로 배치: 막대 -> 원)
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("전 세계 MBTI 유형 평균 비율")
        
        global_avg = df[mbti_cols].mean().sort_values(ascending=False)
        
        # 1. 막대 그래프 (전체 순위)
        st.markdown("##### 📌 전체 유형 순위 (Bar Chart)")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=global_avg.index, y=global_avg.values, palette="viridis", ax=ax)
        ax.set_ylabel("평균 비율")
        plt.xticks(rotation=45, ha='right', fontsize=9)
        st.pyplot(fig)
        
        st.divider() # 구분선
        
        # 2. 원 그래프 (상위 점유율)
        # 원그래프는 너무 넓게 퍼지면 보기 안 좋으므로 중앙 정렬을 위해 컬럼 사용
        c1, c2, c3 = st.columns([1, 2, 1]) # 가운데(2)만 사용
        with c2:
            st.markdown("##### 🥧 상위 유형 점유율 (Pie Chart)")
            fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
            plot_pie_chart(global_avg, "Global Top 8 Types Ratio", ax_pie)
            st.pyplot(fig_pie)

        with st.expander("데이터 자세히 보기"):
            st.dataframe(global_avg.to_frame(name="Global Average Ratio").T)

    # -------------------------------------------------------------------------
    # Tab 2: 국가별 상세 분석 (세로 배치: 막대 -> 원)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("국가별 MBTI 성향 상세")
        
        # 국가 선택
        country_list = df['Country'].unique().tolist()
        default_ix = 0
        if "South Korea" in country_list:
            default_ix = country_list.index("South Korea")
        elif "Korea, South" in country_list:
            default_ix = country_list.index("Korea, South")
            
        selected_country = st.selectbox("분석할 국가를 선택하세요:", country_list, index=default_ix)
        
        # 데이터 추출
        country_data = df[df['Country'] == selected_country][mbti_cols].T
        country_data.columns = ['Ratio']
        country_series = country_data['Ratio'].sort_values(ascending=False)
        
        # 요약 정보 표시
        top_type = country_series.index[0]
        top_val = country_series.values[0]
        st.info(f"💡 **{selected_country}**에서 가장 흔한 유형은 **{top_type}**이며, 약 **{top_val*100:.1f}%**를 차지합니다.")

        # 1. 막대 그래프
        st.markdown(f"##### 📊 {selected_country} - 전체 분포")
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        sns.barplot(x=country_series.index, y=country_series.values, palette="magma", ax=ax2)
        ax2.set_ylabel("비율")
        plt.xticks(rotation=45, ha='right', fontsize=9)
        st.pyplot(fig2)
        
        st.divider() # 구분선

        # 2. 원 그래프
        c1, c2, c3 = st.columns([1, 2, 1]) # 가운데 정렬
        with c2:
            st.markdown(f"##### 🥧 {selected_country} - 상위 유형 비율")
            fig2_pie, ax2_pie = plt.subplots(figsize=(8, 8))
            plot_pie_chart(country_series, f"{selected_country} Top 8 Types", ax2_pie)
            st.pyplot(fig2_pie)

    # -------------------------------------------------------------------------
    # Tab 3: Top 10 & 한국 비교 (기존 유지)
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("MBTI 유형별 Top 10 국가 및 한국 비교")
        
        target_mbti = st.selectbox("순위를 확인하고 싶은 MBTI 유형을 선택하세요:", mbti_cols)
        
        top_10 = df[['Country', target_mbti]].sort_values(by=target_mbti, ascending=False).head(10)
        korea_row = df[df['Country'].isin(['South Korea', 'Korea, South'])]
        
        col_l, col_r = st.columns([2, 1])
        
        with col_l:
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            colors = ['lightgray'] * len(top_10)
            for i, country in enumerate(top_10['Country']):
                if country in ['South Korea', 'Korea, South']:
                    colors[i] = 'crimson'
                else:
                    colors[i] = 'steelblue'

            sns.barplot(x='Country', y=target_mbti, data=top_10, palette=colors, ax=ax3)
            ax3.set_title(f"Top 10 Countries for {target_mbti}")
            ax3.set_ylabel("비율 (Ratio)")
            plt.xticks(rotation=45)
            st.pyplot(fig3)

        with col_r:
            st.markdown(f"### 🇰🇷 한국 데이터")
            if not korea_row.empty:
                korea_val = korea_row[target_mbti].values[0]
                korea_rank = df[target_mbti].rank(ascending=False).loc[korea_row.index[0]]
                
                st.metric(label="한국 비율", value=f"{korea_val:.4f}")
                st.metric(label="세계 순위", value=f"{int(korea_rank)}위")
                
                if int(korea_rank) <= 10:
                    st.success("🎉 세계 Top 10 진입!")
                else:
                    st.info(f"전체 {len(df)}개국 중 {int(korea_rank)}위")
            else:
                st.warning("한국 데이터를 찾을 수 없습니다.")

else:
    st.stop()
