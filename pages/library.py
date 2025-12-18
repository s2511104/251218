import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="서초구 전자도서관 도서 추천",
    page_icon="📚",
    layout="wide"
)

# ------------------------------------------------------------------------------
# 1. 데이터 로드 및 전처리
# ------------------------------------------------------------------------------
st.cache_data(ttl=600)
def load_data():
    # 구글 스프레드시트 CSV 링크
    sheet_id = "1XC7ECtGVVanxBUX8BsLXlAcCZ2ULi2nZgFTd7BAT9zY"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(url)
        # 데이터가 있다면 랜덤 100개만 우선 추출 (속도 및 다양성 확보)
        if len(df) > 100:
            df = df.sample(n=100)
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df = load_data()

# ------------------------------------------------------------------------------
# 2. 사이드바: 컬럼 매핑 설정 (문제 해결의 핵심!)
# ------------------------------------------------------------------------------
st.sidebar.header("⚙️ 데이터 설정")
st.sidebar.info("데이터가 보이지 않는다면 아래에서 알맞은 항목을 선택해주세요.")

if not df.empty:
    # 컬럼 목록 가져오기
    cols = df.columns.tolist()

    # 1) 기본값을 자동으로 찾기 위한 함수
    def find_col(keywords):
        for c in cols:
            if any(k in c for k in keywords):
                return cols.index(c)
        return 0

    # 2) 사용자가 직접 컬럼을 지정하도록 선택박스 생성
    st.sidebar.markdown("---")
    st.sidebar.write("**📌 엑셀 헤더와 매칭해주세요**")
    
    # 제목 (Title)
    col_title = st.sidebar.selectbox("책 제목(서명)", cols, index=find_col(['서명', '제목', 'Title']))
    
    # 저자 (Author)
    col_author = st.sidebar.selectbox("저자", cols, index=find_col(['저자', '지은이', 'Author']))
    
    # 출판사 (Publisher)
    col_pub = st.sidebar.selectbox("출판사", cols, index=find_col(['출판', '발행', 'Publisher']))
    
    # 분야 (Category) -> 문제 해결 포인트 1
    col_category = st.sidebar.selectbox("분야(카테고리)", cols, index=find_col(['분야', '장르', '주제', 'Category']))
    
    # 자료유형 (Type) -> 문제 해결 포인트 2
    col_type = st.sidebar.selectbox("자료유형(전자책/오디오북)", cols, index=find_col(['유형', '구분', 'Type', 'Format']))
    
    # 이미지 (Image) -> 문제 해결 포인트 3
    col_img = st.sidebar.selectbox("책 표지 이미지 URL", cols, index=find_col(['이미지', 'Image', 'URL', '표지']))

else:
    st.stop() # 데이터 로드 실패 시 중단

# ------------------------------------------------------------------------------
# 3. 메인 화면 UI
# ------------------------------------------------------------------------------
st.title("📚 서초구 전자도서관 도서 검색기")
st.write("랜덤으로 추출된 **100권**의 도서 중에서 추천해 드립니다.")
st.divider()

# 검색 필터 UI
c1, c2 = st.columns(2)

with c1:
    # 선택된 '자료유형' 컬럼의 데이터로 옵션 생성
    types = ['전체'] + list(df[col_type].unique())
    selected_type = st.selectbox(f"자료 유형 ({col_type})", types)

with c2:
    # 선택된 '분야' 컬럼의 데이터로 옵션 생성
    # 자료유형을 먼저 선택했다면 그에 맞는 분야만 필터링
    if selected_type != '전체':
        available_cats = df[df[col_type] == selected_type][col_category].unique()
    else:
        available_cats = df[col_category].unique()
        
    categories = ['전체'] + list(available_cats)
    selected_category = st.selectbox(f"분야 ({col_category})", categories)

# 추천 버튼
if st.button("🔍 도서 추천받기", use_container_width=True):
    st.divider()
    
    # 필터링 로직
    result_df = df.copy()
    if selected_type != '전체':
        result_df = result_df[result_df[col_type] == selected_type]
    if selected_category != '전체':
        result_df = result_df[result_df[col_category] == selected_category]
        
    # 결과 출력
    if len(result_df) == 0:
        st.warning("조건에 맞는 도서가 없습니다.")
    else:
        # 최대 3권 랜덤 추천
        sample_n = min(3, len(result_df))
        recs = result_df.sample(n=sample_n)
        
        st.subheader(f"🎉 추천 도서 {sample_n}권")
        
        for _, row in recs.iterrows():
            with st.container():
                col_img_area, col_txt_area = st.columns([1, 4])
                
                # 이미지 출력 처리
                with col_img_area:
                    img_url = str(row[col_img])
                    # URL이 http로 시작하는지 확인 (빈 값이나 에러 방지)
                    if img_url.startswith('http'):
                        st.image(img_url, use_container_width=True)
                    else:
                        st.markdown("🖼️<br>이미지 없음", unsafe_allow_html=True)
                
                # 텍스트 정보 출력
                with col_txt_area:
                    st.markdown(f"### {row[col_title]}")
                    st.markdown(f"**저자:** {row[col_author]} | **출판사:** {row[col_pub]}")
                    st.markdown(f"**분야:** {row[col_category]} | **유형
