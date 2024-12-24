import requests
from bs4 import BeautifulSoup

def crawl_news_by_country(country_name):
    # 크롤링할 URL 예시 (수정 필요)
    url = f"https://example.com/news?query={country_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    for item in soup.select(".news-item"):  # HTML 구조에 맞는 선택자 사용
        title = item.select_one(".title").text.strip()
        summary = item.select_one(".summary").text.strip()
        link = item.select_one("a")["href"]
        news_items.append({"title": title, "summary": summary, "link": link})

    return news_items