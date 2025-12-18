
import streamlit as st
import pandas as pd
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="서초구 전자도서관 도서 추천",
    page_icon="📚",
    layout="centered"
)

# ------------------------------------------------------------------------------
# 1. 데이터 로드 및 전처리 (캐싱 적용)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=600)  # 10분마다 데이터 갱신
def load_and_sample_data():
    # 구글 스프레드시트의 CSV 내보내기 링크
    sheet_id = "1XC7ECtGVVanxBUX8BsLXlAcCZ2ULi2nZgFTd7BAT9zY"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(url)
        
        # ----------------------------------------------------------------------
        # [중요] 데이터 컬럼 매핑
        # 시트의 실제 헤더 이름이 코드와 다를 경우 여기서 수정해야 합니다.
        # 예상 헤더: 서명, 저자, 출판사, 자료유형, 분야, 이미지URL
        # ----------------------------------------------------------------------
        # 데이터 처리를 위해 컬럼명을 영문으로 통일 (실제 시트 헤더에 맞춰 수정 필요)
        # 만약 시트 헤더가 한글이라면 아래처럼 rename을 수행합니다.
        # 여기서는 시트 구조를 추정하여 매핑합니다. 
        # (실제 시트 헤더를 확인하기 어려워 일반적인 명칭으로 매핑 시도)
        
        # 데이터프레임의 컬럼이 충분한지 확인
        if len(df.columns) < 5:
            st.error("데이터 형식이 올바르지 않습니다. 구글 시트의 헤더를 확인해주세요.")
            return pd.DataFrame()

        # 무작위 100개 추출 (데이터가 100개 미만이면 전체 사용)
        if len(df) > 100:
            df = df.sample(n=100)
            
        return df
        
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 데이터 로드
raw_df = load_and_sample_data()

# ------------------------------------------------------------------------------
# 2. UI 및 로직 구현
# ------------------------------------------------------------------------------
st.title("📚 서초구 전자도서관 도서 검색기")
st.markdown("랜덤으로 선정된 **100권의 도서** 중에서 취향에 맞는 책을 찾아보세요!")
st.divider()

if not raw_df.empty:
    # (1) 검색 필터 영역
    col1, col2 = st.columns(2)
    
    with col1:
        # 자료유형 선택 (오디오북, 전자책 등)
        # 데이터에 '자료유형' 컬럼이 있다고 가정하고 unique 값 추출
        # 실제 컬럼명을 모를 경우를 대비해 예외처리
        type_col = [c for c in raw_df.columns if '유형' in c or 'Type' in c]
        if type_col:
            types = ['전체'] + list(raw_df[type_col[0]].unique())
            selected_type = st.selectbox("자료 유형 선택", types)
        else:
            selected_type = '전체'
            st.warning("'자료유형' 컬럼을 찾을 수 없습니다.")

    with col2:
        # 분야 선택
        # 데이터에 '분야', '장르', '카테고리' 등이 포함된 컬럼 찾기
        cat_col = [c for c in raw_df.columns if '분야' in c or '장르' in c or 'Category' in c]
        if cat_col:
            # 유형이 선택되었다면 해당 유형에 있는 분야만 필터링해서 보여줌
            if selected_type != '전체':
                filtered_by_type = raw_df[raw_df[type_col[0]] == selected_type]
                categories = ['전체'] + list(filtered_by_type[cat_col[0]].unique())
            else:
                categories = ['전체'] + list(raw_df[cat_col[0]].unique())
            
            selected_category = st.selectbox("분야 선택", categories)
        else:
            selected_category = '전체'
            st.warning("'분야' 컬럼을 찾을 수 없습니다.")

    # (2) 추천 버튼
    if st.button("🔍 맞춤 도서 추천받기", use_container_width=True):
        st.divider()
        
        # 필터링 로직
        filtered_df = raw_df.copy()
        
        if selected_type != '전체' and type_col:
            filtered_df = filtered_df[filtered_df[type_col[0]] == selected_type]
            
        if selected_category != '전체' and cat_col:
            filtered_df = filtered_df[filtered_df[cat_col[0]] == selected_category]
            
        # 결과 출력
        if len(filtered_df) == 0:
            st.info("조건에 맞는 도서가 없습니다. 다른 조건을 선택해보세요.")
        else:
            # 랜덤 3권 추천 (데이터가 3권 미만이면 전체)
            sample_size = min(3, len(filtered_df))
            recommendations = filtered_df.sample(n=sample_size)
            
            # 컬럼명 자동 탐지 (제목, 저자, 출판사, 이미지)
            title_c = next((c for c in raw_df.columns if '서명' in c or '제목' in c), raw_df.columns[0])
            auth_c = next((c for c in raw_df.columns if '저자' in c), raw_df.columns[1])
            pub_c = next((c for c in raw_df.columns if '출판' in c), raw_df.columns[2])
            img_c = next((c for c in raw_df.columns if '이미지' in c or 'URL' in c), None)

            st.subheader(f"🎉 {sample_size}권의 책을 추천해 드립니다!")
            
            for _, row in recommendations.iterrows():
                with st.container():
                    c1, c2 = st.columns([1, 3])
                    
                    # 이미지 표시
                    with c1:
                        if img_c and str(row[img_c]).startswith('http'):
                            st.image(row[img_c], use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/150x200?text=No+Image", use_container_width=True)
                    
                    # 정보 및 요약 표시
                    with c2:
                        st.markdown(f"### {row[title_c]}")
                        st.markdown(f"**저자:** {row[auth_c]} | **출판사:** {row[pub_c]}")
                        
                        # 한줄 요약 생성 (데이터에 요약이 없으므로 메타데이터 활용)
                        summary_text = (
                            f"이 책은 {row[cat_col[0]] if cat_col else '추천'} 분야의 도서입니다. "
                            f"{row[auth_c]} 작가의 통찰이 담긴 작품으로, {selected_type if selected_type != '전체' else '전자도서관'}에서 만나보실 수 있습니다."
                        )
                        st.info(f"💡 {summary_text}")
                
                st.markdown("---")

else:
    st.write("데이터를 불러오는 중이거나 데이터가 비어있습니다.")
