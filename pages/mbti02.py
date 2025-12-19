import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import os
import urllib.request

# -----------------------------------------------------------------------------
# 1. 한글 폰트 설정 (스트림릿 클라우드 대응)
# -----------------------------------------------------------------------------
def setup_korean_font():
    # 나눔고딕 폰트 파일 다운로드 (없을 경우)
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    font_name = "NanumGothic.ttf"
    
    if not os.path.exists(font_name):
        urllib.request.urlretrieve(font_url, font_name)
    
    # 폰트 등록
    font_entry = fm.FontEntry(fname=font_name, name='NanumGothic')
    fm.fontManager.ttflist.append(font_entry)
    
    # 그래프 기본 설정
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# -----------------------------------------------------------------------------
# 2. 국가명 한글 매핑 데이터
# -----------------------------------------------------------------------------
country_map = {
    'South Korea': '대한민국', 'Korea, South': '대한민국',
    'United States': '미국', 'Japan': '일본', 'China': '중국',
    'Russia': '러시아', 'Germany': '독일', 'France': '프랑스',
    'United Kingdom': '영국', 'Italy': '이탈리아', 'Canada': '캐나다',
    'Australia': '호주', 'Brazil': '브라질', 'India': '인도',
    'Spain': '스페인', 'Mexico': '멕시코', 'Indonesia': '인도네시아',
    'Turkey': '터키', 'Netherlands': '네덜란드', 'Switzerland': '스위스',
    'Sweden': '스웨덴', 'Poland': '폴란드', 'Belgium': '벨기에',
    'Thailand': '태국', 'Vietnam': '베트남', 'Philippines': '필리핀',
    'Malaysia': '말레이시아', 'Singapore': '싱가포르', 'Taiwan': '대만',
    'Afghanistan': '아프가니스탄', 'Ukraine': '우크라이나', 'Egypt': '이집트',
    'Iran': '이란', 'Iraq': '이라크', 'Saudi Arabia': '사우디아라비아',
    'Argentina': '아르헨티나', 'Chile': '칠레', 'Colombia': '콜롬비아',
    'Peru': '페루', 'South Africa': '남아공', 'Nigeria': '나이지리아',
    'Kenya': '케냐', 'New Zealand': '뉴질랜드', 'Greece': '그리스',
    'Portugal': '포르투갈', 'Austria': '오스트리아', 'Norway': '노르웨이',
    'Finland': '핀란드', 'Denmark': '덴마크', 'Ireland': '아일랜드',
    'Czech Republic': '체코', 'Hungary': '헝가리', 'Romania': '루마니아'
}
# (필요시 사전을 더 추가하거나, 없는 국가는 영어 그대로 출력됩니다)

# -----------------------------------------------------------------------------
# 3. 페이지 기본 설정 및 데이터 로드
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="세계 MBTI 성향 분석",
    page_icon="🧠",
    layout="wide"
)

# 스타일 설정 후 한글 폰트 적용
plt.style.use('seaborn-v0_8-whitegrid')
setup_korean_font()

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('mbti_data.csv')
        # 국가명 한글 변환 적용
        df['Country'] = df['Country'].map(country_map).fillna(df['Country'])
        return df
    except FileNotFoundError:
        st.error("❌ 'mbti_data.csv' 파일을 찾을 수 없습니다. 같은 폴더에 파일을 위치시켜주세요.")
        return None

# -----------------------------------------------------------------------------
# 원그래프 그리기 도우미 함수 (Top 8 + 기타)
# -----------------------------------------------------------------------------
def plot_pie_chart(data_series, title, ax):
    data_sorted = data_series.sort_values(ascending=False)
    
    # 상위 8개 추출
    top_n = 8
    if len(data_sorted) > top_n:
        top_slice = data_sorted[:top_n]
        others_value = data_sorted[top_n:].sum()
        # Series 이름 변경 (한글화)
        top_slice['기타(Others)'] = others_value
    else:
        top_slice = data_sorted

    wedges, texts, autotexts = ax.pie(
        top_slice, 
        labels=top_slice.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=sns.color_palette("pastel"),
        wedgeprops={'edgecolor': 'white'}
    )
    
    ax.set_title(title, pad=20, fontsize=14, fontweight='bold')
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
    # Tab 1: 전체 국가 평균
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("전 세계 MBTI 유형 평균 비율")
        
        global_avg = df[mbti_cols].mean().sort_values(ascending=False)
        
        # 1. 막대 그래프
        st.markdown("##### 📌 전체 유형 순위 (막대그래프)")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=global_avg.index, y=global_avg.values, palette="viridis", ax=ax)
        
        ax.set_ylabel("평균 비율", fontsize=12)
        ax.set_xlabel("MBTI 유형", fontsize=12)
        ax.set_title("전 세계 MBTI 유형별 평균 비율", fontsize=15)
        
        plt.xticks(rotation=45, ha='right', fontsize=9)
        st.pyplot(fig)
        
        st.divider()
        
        # 2. 원 그래프
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("##### 🥧 상위 유형 점유율 (원그래프)")
            fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
            plot_pie_chart(global_avg, "전 세계 상위 8개 유형 비율", ax_pie)
            st.pyplot(fig_pie)

        with st.expander("데이터 자세히 보기"):
            st.dataframe(global_avg.to_frame(name="평균 비율").T)

    # -------------------------------------------------------------------------
    # Tab 2: 국가별 상세 분석
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("국가별 MBTI 성향 상세")
        
        country_list = df['Country'].unique().tolist()
        default_ix = 0
        if "대한민국" in country_list:
            default_ix = country_list.index("대한민국")
            
        selected_country = st.selectbox("분석할 국가를 선택하세요:", country_list, index=default_ix)
        
        # 데이터 추출
        country_data = df[df['Country'] == selected_country][mbti_cols].T
        country_data.columns = ['Ratio']
        country_series = country_data['Ratio'].sort_values(ascending=False)
        
        top_type = country_series.index[0]
        top_val = country_series.values[0]
        st.info(f"💡 **{selected_country}**에서 가장 흔한 유형은 **{top_type}**이며, 약 **{top_val*100:.1f}%**를 차지합니다.")

        # 1. 막대 그래프
        st.markdown(f"##### 📊 {selected_country} - 전체 분포")
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        sns.barplot(x=country_series.index, y=country_series.values, palette="magma", ax=ax2)
        
        ax2.set_ylabel("비율", fontsize=12)
        ax2.set_xlabel("MBTI 유형", fontsize=12)
        ax2.set_title(f"{selected_country}의 MBTI 유형 분포", fontsize=15)
        
        plt.xticks(rotation=45, ha='right', fontsize=9)
        st.pyplot(fig2)
        
        st.divider()

        # 2. 원 그래프
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(f"##### 🥧 {selected_country} - 상위 유형 비율")
            fig2_pie, ax2_pie = plt.subplots(figsize=(8, 8))
            plot_pie_chart(country_series, f"{selected_country} 상위 8개 유형", ax2_pie)
            st.pyplot(fig2_pie)

    # -------------------------------------------------------------------------
    # Tab 3: Top 10 & 한국 비교
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("MBTI 유형별 Top 10 국가 및 한국 비교")
        
        target_mbti = st.selectbox("순위를 확인하고 싶은 MBTI 유형을 선택하세요:", mbti_cols)
        
        top_10 = df[['Country', target_mbti]].sort_values(by=target_mbti, ascending=False).head(10)
        korea_row = df[df['Country'] == '대한민국']
        
        col_l, col_r = st.columns([2, 1])
        
        with col_l:
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            colors = ['lightgray'] * len(top_10)
            for i, country in enumerate(top_10['Country']):
                if country == '대한민국':
                    colors[i] = 'crimson'
                else:
                    colors[i] = 'steelblue'

            sns.barplot(x='Country', y=target_mbti, data=top_10, palette=colors, ax=ax3)
            
            ax3.set_title(f"{target_mbti} 유형 비율 상위 10개국", fontsize=15)
            ax3.set_ylabel("비율", fontsize=12)
            ax3.set_xlabel("국가", fontsize=12)
            
            plt.xticks(rotation=45, fontsize=10)
            st.pyplot(fig3)

        with col_r:
            st.markdown(f"### 🇰🇷 대한민국 현황")
            if not korea_row.empty:
                korea_val = korea_row[target_mbti].values[0]
                korea_rank = df[target_mbti].rank(ascending=False).loc[korea_row.index[0]]
                
                st.metric(label="대한민국 비율", value=f"{korea_val:.4f}")
                st.metric(label="세계 순위", value=f"{int(korea_rank)}위 / {len(df)}개국")
                
                if int(korea_rank) <= 10:
                    st.success(f"🎉 대한민국은 **{target_mbti}** 비율 세계 Top 10 입니다!")
                else:
                    st.info(f"전체 {len(df)}개국 중 {int(korea_rank)}위입니다.")
            else:
                st.warning("데이터에서 '대한민국(South Korea)' 정보를 찾을 수 없습니다.")

else:
    st.stop()
