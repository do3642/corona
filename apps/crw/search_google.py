import requests
from bs4 import BeautifulSoup

def search_google(query):
    # Google 뉴스 검색 URL 생성
    url = f"https://www.google.com/search?q={query}&tbm=nws"

    # 요청 헤더 정의 (브라우저처럼 위장)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # HTTP 요청
    response = requests.get(url, headers=headers)
    
    # 요청 성공 여부 확인
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return []
    
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 데이터를 저장할 리스트
    news = []

    # Google 뉴스 검색 결과 선택
    # <h3 class="LC20lb MBeuO DKV0Md"> 제목 </h3>
    for item in soup.select('div.BVG0Nb'):  # 각 뉴스 컨테이너를 감싸는 요소
        title_tag = item.select_one('h3.LC20lb.MBeuO.DKV0Md')  # 제목 태그 선택
        link_tag = item.select_one('a')  # 링크 태그 선택
        
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)  # 제목 텍스트 추출
            link = link_tag['href']  # 링크 URL
            
            # 설명 텍스트 (선택 사항)
            snippet_tag = item.select_one('div.GI74Re')  # 요약 정보 클래스
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else "요약 없음"
            
            # 뉴스 데이터 추가
            news.append({
                'title': title,
                'url': link,
                'snippet': snippet
            })

    # 결과 반환
    return news

# 테스트 실행
query = "COVID-19 updates"
news_results = search_google(query)

# 결과 출력
for news in news_results:
    print(f"Title: {news['title']}")
    print(f"URL: {news['url']}")
    print(f"Snippet: {news['snippet']}")
    print("=" * 50)