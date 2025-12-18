import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------
# 1. 페이지 설정
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="서초구 전자도서관 검색기",
    page_icon="📚",
    layout="wide"
)

# ------------------------------------------------------------------------------
# 2. 데이터 로드 함수
# ------------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    # 구글 스프레드시트 CSV 내보내기 링크
    sheet_id = "1XC7ECtGVVanxBUX8BsLXlAcCZ2ULi2nZgFTd7BAT9zY"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(url)
        # 데이터가 100개보다 많으면 랜덤으로 100개만 추출
        if len(df) > 100:
            df = df.sample(n=100)
        return df
    except Exception as e:
        return None

# 데이터 불러오기 실행
df = load_data()

# ------------------------------------------------------------------------------
# 3. 사이드바 설정을 통한 오류 해결 (매우 중요)
# ------------------------------------------------------------------------------
st.sidebar.title("⚙️ 설정")
st.sidebar.info("책 정보가 안 보이면 아래에서 항목을 맞춰주세요.")

if df is not None and not df.empty:
    cols = df.columns.tolist()

    # 컬럼 자동 찾기 헬퍼 함수
    def get_index(keywords, columns):
        for i, col in enumerate(columns):
            for k in keywords:
                if k in col:
                    return i
        return 0

    st.sidebar.markdown("### 1. 엑셀 컬럼 연결")
    
    # 각 항목에 대해 엑셀의 어느 열을 사용할지 선택 (기본값 자동 매칭 시도)
    col_title = st.sidebar.selectbox("책 제목", cols, index=get_index(['서명', '제목', 'Title'], cols))
    col_author = st.sidebar.selectbox("저자", cols, index=get_index(['저자', '지은이', 'Author'], cols))
    col_pub = st.sidebar.selectbox("출판사", cols, index=get_index(['출판', '발행', 'Publisher'], cols))
    col_category = st.sidebar.selectbox("분야(장르)", cols, index=get_index(['분야', '장르', '주제', 'Category'], cols))
    col_type = st.sidebar.selectbox("자료유형(오디오북/전자책)", cols, index=get_index(['유형', '구분', 'Type'], cols))
    col_img = st.sidebar.selectbox("이미지 URL", cols, index=get_index(['이미지', 'Image', 'URL', '표지'], cols))

    # --------------------------------------------------------------------------
    # 4. 메인 화면 구현
    # --------------------------------------------------------------------------
    st.title("📚 서초구 전자도서관 도서 검색기")
    st.markdown("랜덤으로 선정된 **100권**의 도서 중에서 추천해 드립니다.")
    st.divider()

    # 검색 필터 (2단 구성)
    c1, c2 = st.columns(2)
    
    with c1:
        # 자료 유형 선택
        types = ['전체'] + list(df[col_type].unique())
        selected_type = st.selectbox("자료 유형 선택", types)
    
    with c2:
        # 분야 선택 (자료 유형에 따라 연동)
        if selected_type != '전체':
            available_cats = df[df[col_type] == selected_type][col_category].unique()
        else:
            available_cats = df[col_category].unique()
        
        cats = ['전체'] + list(available_cats)
        selected_category = st.selectbox("분야 선택", cats)

    # 추천 버튼 클릭 시 동작
    if st.button("🔍 도서 추천받기", use_container_width=True):
        st.divider()
        
        # 필터링
        filtered_df = df.copy()
        if selected_type != '전체':
            filtered_df = filtered_df[filtered_df[col_type] == selected_type]
        if selected_category != '전체':
            filtered_df = filtered_df[filtered_df[col_category] == selected_category]
            
        # 결과 표시
        if filtered_df.empty:
            st.warning("조건에 맞는 도서가 없습니다.")
        else:
            # 최대 3권 랜덤
            sample_count = min(3, len(filtered_df))
            results = filtered_df.sample(n=sample_count)
            
            st.subheader(f"🎉 추천 도서 {sample_count}권")
            
            for index, row in results.iterrows():
                # 카드 형태의 레이아웃
                with st.container():
                    col_img_view, col_info_view = st.columns([1, 3])
                    
                    # 이미지 표시
                    with col_img_view:
                        img_link = str(row[col_img])
                        if img_link.startswith("http"):
                            st.image(img_link, use_container_width=True)
                        else:
                            st.text("이미지 없음")
                    
                    # 정보 표시
                    with col_info_view:
                        st.markdown(f"### {row[col_title]}")
                        st.text(f"저자: {row[col_author]} | 출판사: {row[col_pub]}")
                        st.caption(f"분야: {row[col_category]} | 유형: {row[col_type]}")
                        
                        # 한줄 요약 (데이터 조합)
                        summary = f"이 책은 {row[col_category]} 분야에서 주목받는 도서입니다. {row[col_author]} 작가의 이야기를 통해 새로운 영감을 얻어보세요."
                        st.info(summary)
                
                st.markdown("---")

else:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
