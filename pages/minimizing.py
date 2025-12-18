import streamlit as st
import urllib.parse

# 페이지 기본 설정
st.set_page_config(
    page_title="축제 물품 최저가 탐색기",
    page_icon="🎉",
    layout="centered"
)

# 제목 및 설명
st.title("🎉 축제 물품 최저가 탐색기")
st.write("각 쇼핑몰의 **최저가 정렬** 검색 결과로 바로 연결해 드립니다.")
st.caption("※ 외부 라이브러리 설치 제한으로 인해 실시간 크롤링 대신 '바로가기' 기능을 제공합니다.")

st.markdown("---")

# 검색할 물품 리스트 (상품명과 검색 키워드)
items = [
    {
        "display_name": "Take Alive 머스캣 청포도 120ml",
        "keyword": "테이크 얼라이브 머스캣 120ml",
        "image": "🧃"
    },
    {
        "display_name": "매일우유 1L",
        "keyword": "매일우유 1L",
        "image": "🥛"
    },
    {
        "display_name": "미떼 오리지날 핫초코 30g x 10개입",
        "keyword": "미떼 오리지날 핫초코 30g 10개",
        "image": "☕"
    }
]

# 쇼핑몰별 검색 URL 생성 함수 (최저가 정렬 파라미터 포함)
def get_search_links(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    
    # 쿠팡: sorter=salePriceAsc (가격 낮은순)
    coupang_url = f"https://www.coupang.com/np/search?component=&q={encoded_keyword}&channel=user&sorter=salePriceAsc"
    
    # G마켓: s=1 (가격 낮은순)
    gmarket_url = f"https://browse.gmarket.co.kr/search?keyword={encoded_keyword}&s=1"
    
    # 11번가: sortCd=L (가격 낮은순)
    st11_url = f"https://search.11st.co.kr/Search.tmall?kwd={encoded_keyword}&sortCd=L"
    
    return coupang_url, gmarket_url, st11_url

# 메인 UI 루프
for item in items:
    # 각 아이템별 컨테이너 생성
    with st.container():
        st.subheader(f"{item['image']} {item['display_name']}")
        
        # 3개의 컬럼으로 나누어 버튼 배치
        col1, col2, col3 = st.columns(3)
        
        coupang, gmarket, st11 = get_search_links(item['keyword'])
        
        with col1:
            st.link_button(
                label="쿠팡 최저가 보기",
                url=coupang,
                help="쿠팡에서 낮은 가격순으로 검색합니다."
            )
            
        with col2:
            st.link_button(
                label="G마켓 최저가 보기",
                url=gmarket,
                help="G마켓에서 낮은 가격순으로 검색합니다."
            )
            
        with col3:
            st.link_button(
                label="11번가 최저가 보기",
                url=st11,
                help="11번가에서 낮은 가격순으로 검색합니다."
            )
            
    st.divider() # 구분선

# 하단 정보
st.info("💡 각 버튼을 누르면 해당 쇼핑몰의 '낮은 가격순' 검색 페이지가 새 탭에서 열립니다.")
