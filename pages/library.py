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
# 2. 데이터 로드 (전체 데이터 가져오기)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    sheet_id = "1XC7ECtGVVanxBUX8BsLXlAcCZ2ULi2nZgFTd7BAT9zY"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        # 전체 데이터를 읽어옵니다 (샘플링 제거)
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

df = load_data()

# ------------------------------------------------------------------------------
# 3. 사이드바: 컬럼 매핑 (F열, G열 우선 적용)
# ------------------------------------------------------------------------------
st.sidebar.title("⚙️ 데이터 설정")

if df is not None and not df.empty:
    cols = df.columns.tolist()
    
    # 헬퍼 함수: 인덱스가 범위를 벗어나지 않도록 안전하게 반환
    def safe_index(idx, max_len):
        return idx if idx < max_len else 0

    # 1. 자료유형 (F열 -> 인덱스 5)
    # 엑셀은 A=0, B=1, ... F=5
    default_type_idx = safe_index(5, len(cols))
    col_type = st.sidebar.selectbox("자료유형 (F열)", cols, index=default_type_idx)

    # 2. 분야 (G열 -> 인덱스 6)
    default_cat_idx = safe_index(6, len(cols))
    col_category = st.sidebar.selectbox("분야 (G열)", cols, index=default_cat_idx)

    st.sidebar.markdown("---")
    st.sidebar.info("나머지 정보가 안 맞으면 아래에서 조정해주세요.")

    # 나머지 컬럼 자동 매칭 시도
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
    # 4. 메인 화면: 검색 및 추천
    # --------------------------------------------------------------------------
    st.title("📚 서초구 전자도서관 도서 검색기")
    
    # 전체 데이터 건수 표시
    st.markdown(f"현재 등록된 **{len(df):,}권**의 도서 데이터를 모두 탐색합니다.")
    st.divider()

    # (1) 검색 필터 구성
    c1, c2 = st.columns(2)
    
    with c1:
        # F열의 고유값 추출 (오디오북, 전자책 등)
        types = ['전체'] + sorted(list(df[col_type].dropna().unique()))
        selected_type = st.selectbox(f"자료 유형 선택 ({col_type})", types)
    
    with c2:
        # G열의 고유값 추출 (분야)
        # 유형 선택에 따라 분야 목록을 필터링하여 보여줌 (선택 편의성)
        if selected_type != '전체':
            filtered_by_type = df[df[col_type] == selected_type]
            available_cats = filtered_by_type[col_category].dropna().unique()
        else:
            available_cats = df[col_category].dropna().unique()
        
        cats = ['전체'] + sorted(list(available_cats))
        selected_category = st.selectbox(f"분야 선택 ({col_category})", cats)

    # (2) 추천 버튼
    if st.button("🔍 맞춤 도서 추천받기", use_container_width=True):
        st.divider()
        
        # 데이터 필터링
        result_df = df.copy()
        
        if selected_type != '전체':
            result_df = result_df[result_df[col_type] == selected_type]
            
        if selected_category != '전체':
            result_df = result_df[result_df[col_category] == selected_category]
            
        # 결과 처리
        if result_df.empty:
            st.warning("조건에 맞는 도서가 없습니다. 다른 조건을 선택해보세요.")
        else:
            # 검색된 책 중에서 랜덤 3권 추출
            count = min(3, len(result_df))
            recommendations = result_df.sample(n=count)
            
            st.subheader(f"🎉 추천 도서 {count}권 (총 {len(result_df)}권 중 선정)")
            
            for i, row in recommendations.iterrows():
                with st.container():
                    col_img_view, col_info_view = st.columns([1, 4])
                    
                    # 이미지 표시
                    with col_img_view:
                        img_url = str(row[col_img])
                        if img_url.startswith("http"):
                            st.image(img_url, use_container_width=True)
                        else:
                            st.markdown("🖼️<br>이미지 없음", unsafe_allow_html=True)
                    
                    # 텍스트 정보 표시
                    with col_info_view:
                        st.markdown(f"### {row[col_title]}")
                        st.markdown(f"**저자:** {row[col_author]} | **출판사:** {row[col_pub]}")
                        st.caption(f"분야: {row[col_category]} | 유형: {row[col_type]}")
                        
                        # 자동 생성 요약 문구
                        summary = f"이 도서는 '{row[col_category]}' 분야의 책입니다. {row[col_author]} 작가의 작품을 찾고 계셨다면 이 책을 추천합니다."
                        st.info(summary)
                        
                st.markdown("---")

else:
    st.error("데이터를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
