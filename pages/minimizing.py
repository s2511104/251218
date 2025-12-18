import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="축제 물품 최저가 탐색기",
    page_icon="🎉",
    layout="centered"
)

st.title("🎉 축제 물품 최저가 탐색기")
st.write("원하는 물품을 선택하면 각 쇼핑몰의 **최저가 검색 결과**로 연결됩니다.")
st.markdown("---")

# 물품 데이터 (표시 이름 : 검색 키워드)
items = {
    "🧃 Take Alive 머스캣 청포도 120ml": "테이크 얼라이브 머스캣 120ml",
    "🥛 매일우유 1L": "매일우유 1L",
    "☕ 미떼 오리지날 핫초코 30g x 10개입": "미떼 오리지날 핫초코 30g 10개"
}

# 1. 선택 박스 (Selectbox)
selected_item_name = st.selectbox(
    "검색할 물품을 선택해주세요 👇",
    options=list(items.keys()),
    index=None,
    placeholder="여기를 눌러 물품을 선택하세요..."
)

# 2. 선택 시 버튼 표시
if selected_item_name:
    # 선택된 이름에 맞는 검색 키워드 가져오기
    raw_keyword = items[selected_item_name]
    
    # URL 생성을 위한 간단한 처리 (공백을 +로 변경)
    # 라이브러리 없이 브라우저가 인식하도록 처리
    search_keyword = raw_keyword.replace(" ", "+")
    
    # 각 쇼핑몰 검색 링크 직접 생성 (최저가 정렬 파라미터 포함)
    coupang_url = f"https://www.coupang.com/np/search?component=&q={search_keyword}&channel=user&sorter=salePriceAsc"
    gmarket_url = f"https://browse.gmarket.co.kr/search?keyword={search_keyword}&s=1"
    st11_url = f"https://search.11st.co.kr/Search.tmall?kwd={search_keyword}&sortCd=L"
    
    st.divider()
    st.subheader(f"{selected_item_name}")
    st.caption("아래 버튼을 누르면 새 탭에서 최저가 정렬 결과를 볼 수 있습니다.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.link_button("쿠팡 최저가", coupang_url, use_container_width=True)
    with col2:
        st.link_button("G마켓 최저가", gmarket_url, use_container_width=True)
    with col3:
        st.link_button("11번가 최저가", st11_url, use_container_width=True)

else:
    st.info("👆 위 박스에서 물품을 선택하면 최저가 버튼이 나타납니다.")
