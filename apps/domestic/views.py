from flask import Blueprint, render_template, redirect
import folium
import requests
from bs4 import BeautifulSoup

bp = Blueprint(
  "domestic",
  __name__,
  template_folder="templates",
  static_folder="static"
  )

@bp.route('/')
def index():
  # 지도가 전국이 다 보일 수 있도록 설정.
  map = folium.Map( location=[36, 128.00025], zoom_start=7.25, tiles="CartoDB positron")
  
  map_html = map._repr_html_()

  return render_template('domestic/index.html', map_html = map_html)


@bp.route('/crawling')
def crawling():
  response = requests.get(f'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query=코로나')

  html = response.text
  soup = BeautifulSoup(html, 'html.parser')

  links = soup.select(".news_tit")
  articles = []
  for link in links[:5]:
    title = link.text
    url = link.attrs['href']
    articles.append({'title': title, 'url': url})

  return render_template('domestic/index.html', articles=articles)