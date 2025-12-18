import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------
# 1. 페이지 설정
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="서초구 전자도서관 전체 검색기",
    page_icon="📚",
    layout="wide"
)

# ------------------------------------------------------------------------------
# 2. 데이터 로드 (전체 데이터)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    sheet_id = "1XC7ECtGVVanxBUX8BsLXlAcCZ2ULi2nZgFTd7BAT9zY"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

df = load_data()

# ------------------------------------------------------------------------------
# 3. 사이드바: 컬럼 매핑 (F열, G열 자동 인식)
# ------------------------------------------------------------------------------
st.sidebar.title("⚙️ 데이터 설정")

if df is not None and not df.empty:
    cols = df.columns.tolist()
    
    # 안전한 인덱스 접근 함수
    def safe_index(idx, max_len):
        return idx if idx < max_len else 0

    # 1. 자료유형 (F열 -> 인덱스 5)
    col_type = st.sidebar.selectbox("자료유형 (F열)", cols, index=safe_index(5, len(cols)))

    # 2. 분야 (G열 -> 인덱스 6)
    col_category = st.sidebar.selectbox("분야 (G열)", cols, index=safe_index(6, len(cols)))

    st.sidebar.markdown("---")
    st.sidebar.info("상세 정보 매핑 (필요시 수정)")

    # 키워드로 컬럼 찾기
    def get_index_by_keyword(keywords, columns):
        for i, col in enumerate(columns):
            for k in keywords:
                if k in col:
                    return i
        return 0

    col_title = st.sidebar.selectbox("책 제목", cols, index=get_index_by_keyword(['서명', '제목', 'Title'], cols))
    col_author = st.sidebar.selectbox("저자", cols, index=get_index_by_keyword(['저자', '지은이', 'Author'], cols))
    col_pub = st.sidebar.selectbox("출판사", cols, index=get_index_by_keyword(['출판', '발행', 'Publisher'], cols))
    col_img = st.sidebar.selectbox("이미지 URL", cols, index=get_index_by_keyword(['이미지', 'Image', 'URL', '표지'], cols))

    # --------------------------------------------------------------------------
    # 4. 메인 화면
    # --------------------------------------------------------------------------
    st.title("📚 서초구 전자도서관 도서 검색기")
    
    st.markdown(f"**전체 도서 {len(df):,}권** 중에서 원하시는 책을 찾아보세요.")
    st.divider()

    # (1) 검색 필터
    c1, c2 = st.columns(2)
    
    with c1:
        # 자료유형 선택
        types = ['전체'] + sorted(list(df[col_type].dropna().unique()))
        selected_type = st.selectbox(f"자료 유형 ({col_type})", types)
    
    with c2:
        # 분야 선택 (유형에 따라 필터링)
        if selected_type != '전체':
            filtered_by_type = df[df[col_type] == selected_type]
            available_cats = filtered_by_type[col_category].dropna().unique()
        else:
            available_cats = df[col_category].dropna().unique()
        
        cats = ['전체'] + sorted(list(available_cats))
        selected_category = st.selectbox(f"분야 ({col_category})", cats)

    # (2) 검색 버튼
    if st.button("🔍 도서 검색", use_container_width=True):
        st.divider()
        
        # 필터링
        result_df = df.copy()
        
        if selected_type != '전체':
            result_df = result_df[result_df[col_type] == selected_type]
            
        if selected_category != '전체':
            result_df = result_df[result_df[col_category] == selected_category]
            
        # 결과 출력
        if result_df.empty:
            st.warning("조건에 맞는 도서가 없습니다.")
        else:
            count = len(result_df)
            st.subheader(f"🎉 검색 결과: 총 {count}권")
            
            # 너무 많은 결과가 한 번에 나오면 브라우저가 느려질 수 있으므로 알림
            if count > 100:
                st.info(f"결과가 많습니다({count}권). 스크롤을 내려 확인하세요.")

            # [수정됨] 3권 제한 없이 전체 리스트 출력
            for i, row in result_df.iterrows():
                with st.container():
                    col_img_view, col_info_view = st.columns([1, 4])
                    
                    # 이미지
                    with col_img_view:
                        img_url = str(row[col_img])
                        if img_url.startswith("http"):
                            st.image(img_url, use_container_width=True)
                        else:
                            st.markdown("🖼️<br>이미지 없음", unsafe_allow_html=True)
                    
                    # 정보
                    with col_info_view:
                        st.markdown(f"### {row[col_title]}")
                        st.markdown(f"**저자:** {row[col_author]} | **출판사:** {row[col_pub]}")
                        st.caption(f"분야: {row[col_category]} | 유형: {row[col_type]}")
                        
                        summary = f"이 책은 {row[col_category]} 분야의 도서입니다."
                        st.info(summary)
                        
                st.markdown("---")

else:
    st.error("데이터를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
