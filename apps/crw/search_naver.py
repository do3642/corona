import requests
from bs4 import BeautifulSoup

def search_naver(query):
    # 네이버 검색 URL 생성
    url = f"https://search.naver.com/search.naver?query={query}"

    # 요청 헤더 정의
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    # 요청 성공 여부 확인
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return []
    
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser')

    
    
    # 뉴스 데이터를 저장할 리스트
    news = []

    # # `.total_wrap` 클래스가 있는 모든 요소를 선택
    for item in soup.select('.total_wrap'):
        # 제목 추출
        title_tag = item.select_one('.total_tit')  # 제목이 있는 태그
        a_tag = title_tag.select_one('.link_tit')
        
        if title_tag:
            title = title_tag.get_text(strip=True)  # 제목 텍스트

            link = a_tag.get('href', '#')  # 'href' 속성이 없으면 기본값 '#' 사용
            
            # 메타데이터 추출 (선택 사항)
            metadata_tag = item.select_one('.name')  # 메타데이터 정보
            metadata = metadata_tag.get_text(strip=True) if metadata_tag else "정보 없음"
            
            # 뉴스 데이터 추가
            news.append({
                'title': title,
                'url': link,
                'metadata': metadata
            })

    # 결과 반환
    return news

