from flask import Blueprint, render_template
import folium
import folium.features
import requests
from bs4 import BeautifulSoup
import json

from apps.domestic.data import sheet_data

bp = Blueprint(
  "domestic",
  __name__,
  template_folder="templates",
  static_folder="static"
  )

@bp.route('/')
def index():
  area_sheet_data = sheet_data.get('시군구별(발생률,사망률)')
  df = area_sheet_data.set_index('시도명')
  df_total = df.query("시군구=='합계'")

  geo_path = 'apps/static/data/korea.json'
  geo_str = json.load(open(geo_path, encoding='utf-8'))

  area_name = 'feature.properies.CTP_KOR_NM'

  # 지도가 전국이 다 보일 수 있도록 설정.
  map = folium.Map( location=[36, 128.00025], zoom_start=7.25, tiles="CartoDB positron")

  # 지역별 코로나 발생률에 따라 지도에 색깔 구분
  folium.Choropleth(geo_data = geo_str,
                 data=df_total,
                 columns=[df_total.index, '발생률\n(인구10만명당, 명)'],
                 key_on = 'feature.properties.CTP_KOR_NM',
                 fill_color = 'YlOrBr',
                 fill_opacity=0.7,
                 line_opacity=0.4,
                 legend_name='지역별 코로나 발생률(인구 10만명당, 명)'
                 ).add_to(map)
  
  # 추가정보를 나타내기 위한 툴팁 설정
  def tooltip_function(region_name):
    if region_name in df_total.index:
     confirmed = int(df_total.loc[region_name, '누적확진자(명)'])
     deaths = int(df_total.loc[region_name, '누적사망자(명)'])
    else:
     confirmed = '데이터 없음'
     deaths = '데이터 없음'

    return f""""
    <div>
      <b>{region_name}</b><br>
      누적 확진자: {confirmed}<br>
      누적 사망자: {deaths}
    </div>
    """
  
  # GeoJson에서 툴팁 기능 추가
  folium.GeoJson(
    geo_str,
    name='지역별 데이터',
    style_function=lambda feature: {
        'weight': 0.1,
        'color': 'black',
    },
    highlight_function=lambda feature: {
        'weight': 1,
        'fillOpacity': 0.3,
    },
    tooltip=folium.features.GeoJsonTooltip(
        fields=['CTP_KOR_NM'],  # JSON 데이터의 key
        aliases=['지역 이름:'],  # 툴팁 레이블
        localize=True,
        labels=True,
        sticky=True
    ),
    popup=folium.Popup(  # 마우스 클릭 시 팝업 표시
        html=lambda feature: tooltip_function(feature),
        max_width=300
    )
  ).add_to(map)



  map_html = map._repr_html_()

  # 코로나 관련 기사 크롤링
  response = requests.get(f'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query=코로나')

  html = response.text
  soup = BeautifulSoup(html, 'html.parser')

  links = soup.select(".news_tit")
  articles = []

  for link in links[:5]:
    title = link.text
    url = link.attrs['href']
    articles.append({'title': title, 'url': url})

  return render_template('domestic/index.html', map_html = map_html, articles = articles)