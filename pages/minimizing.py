네, 이번에는 사용자가 직접 검색어를 입력하면 5개 쇼핑몰(쿠팡, G마켓, 11번가, 롯데홈쇼핑, 옥션)의 최저가 정렬 페이지로 바로 연결해주는 앱을 만들어 드리겠습니다.

물론, import streamlit as st 외에 다른 라이브러리는 일절 사용하지 않았습니다.

아래 코드를 app.py에 복사해서 붙여넣으세요.

Python

import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="통합 최저가 검색기",
    page_icon="🔍",
    layout="wide"  # 버튼이 5개라 넓은 화면 사용
)

# 제목 및 설명
st.title("🛒 쇼핑몰 통합 최저가 검색기")
st.markdown("""
원하는 상품명을 입력하면 **5대 쇼핑몰**의 최저가 페이지를 한 번에 열 수 있습니다.
""")
st.divider()

# 1. 사용자 입력 받기 (텍스트 인풋)
# Enter를 치면 바로 동작합니다.
keyword = st.text_input(
    label="검색할 상품명을 입력하세요",
    placeholder="예: 신라면 20개입, 아이폰 케이스, 32인치 모니터...",
    help="상품명을 구체적으로 적을수록 정확도가 올라갑니다."
)

# 2. 검색어가 있을 때만 버튼 생성
if keyword:
    # URL 생성을 위한 문자열 처리 (공백을 +로 치환)
    # 별도 라이브러리 없이 브라우저 호환성을 위해 처리
    query = keyword.strip().replace(" ", "+")
    
    st.subheader(f"🔍 '{keyword}' 최저가 검색 결과")
    st.caption("아래 버튼을 누르면 각 사이트의 '낮은 가격순' 정렬 페이지가 새 탭에서 열립니다.")
    st.write("") # 여백

    # --- 각 쇼핑몰별 최저가 정렬 URL 패턴 ---
    
    # 1) 쿠팡: sorter=salePriceAsc
    url_coupang = f"https://www.coupang.com/np/search?component=&q={query}&channel=user&sorter=salePriceAsc"
    
    # 2) G마켓: s=1 (낮은 가격순)
    url_gmarket = f"https://browse.gmarket.co.kr/search?keyword={query}&s=1"
    
    # 3) 11번가: sortCd=L (Low Price)
    url_st11 = f"https://search.11st.co.kr/Search.tmall?kwd={query}&sortCd=L"
    
    # 4) 롯데홈쇼핑: s_rank=3 (낮은 가격순)
    url_lotte = f"https://www.lotteimall.com/search/searchMain.lotte?headerQuery={query}&s_rank=3"
    
    # 5) 옥션: s=8 (낮은 가격순)
    url_auction = f"http://browse.auction.co.kr/search?keyword={query}&s=8"

    # --- 버튼 배치 (5개 나란히) ---
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.link_button("🚀 쿠팡", url_coupang, use_container_width=True)
        
    with col2:
        st.link_button("🟢 G마켓", url_gmarket, use_container_width=True)
        
    with col3:
        st.link_button("🔴 11번가", url_st11, use_container_width=True)
        
    with col4:
        st.link_button("🛍️ 롯데홈쇼핑", url_lotte, use_container_width=True)
        
    with col5:
        st.link_button("🟡 옥션", url_auction, use_container_width=True)

    st.success("팁: 배송비를 포함한 실제 가격은 각 사이트 옵션을 확인하세요!")

else:
    # 검색어가 없을 때 보이는 안내 문구
    st.info("👆 위 입력창에 찾으시는 물건을 입력하고 Enter를 눌러주세요.")
