from flask import Blueprint, render_template, request
import folium
import folium.features
import folium.utilities
import requests
from bs4 import BeautifulSoup
import json
import xmltodict

from apps.domestic.data import sheet_data

bp = Blueprint(
  "domestic",
  __name__,
  template_folder="templates",
  static_folder="static"
  )

# 어떤 url에서든지 다 들어갈 자료들
def common_data(area=None):
  # 기사 크롤링
  query = f"코로나+{area}" if area else '코로나'
  response = requests.get(f'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query={query}')

  html = response.text
  soup = BeautifulSoup(html, 'html.parser')

  links = soup.select(".news_tit")
  articles = []

  for link in links[:7]:
    title = link.text
    url = link.attrs['href']
    articles.append({'title': title, 'url': url})

  return articles


@bp.route('/')
def index():
  # 코로나 기사 크롤링
  articles = common_data()

  area_sheet_data = sheet_data.get('시군구별(발생률,사망률)')
  df = area_sheet_data.set_index('시도명')
  df_total = df.query("시군구=='합계'")

  geo_path = 'apps/static/data/korea.json'
  geo_str = json.load(open(geo_path, encoding='utf-8'))

  # 지도가 전국이 다 보일 수 있도록 설정.
  map = folium.Map( location=[35.75, 128.00025], zoom_start=6.9)

  # 지역별 코로나 발생률에 따라 지도에 색깔 구분
  folium.Choropleth(geo_data = geo_str,
                 data=df_total,
                 columns=[df_total.index, '발생률\n(인구10만명당, 명)'],
                 key_on = 'feature.properties.CTP_KOR_NM',
                 fill_color = 'YlOrBr',
                 fill_opacity=0.7,
                 line_opacity=0.4,
                 legend_name='지역별 코로나 발생률(인구 10만명당, 명)',
                 highlight=False
                 ).add_to(map)
  
  # 누적 확진자랑 사망자 데이터를 json 파일에 추가
  for feature in geo_str['features']:
    region_name = feature['properties']['CTP_KOR_NM']
    if region_name in df_total.index:
      feature['properties']['confirmed'] = int(df_total.loc[region_name, '누적확진자(명)'])
      feature['properties']['deaths'] = int(df_total.loc[region_name, '누적사망자(명)'])
    else:
      feature['properties']['confirmed'] = '데이터 없음'
      feature['properties']['deaths'] = '데이터 없음'

  # 클릭 했을 때 나타나는 검정색 네모 없애주는 css
  map.get_root().html.add_child(folium.Element("""
  <style>
      .leaflet-interactive {
          outline: none !important;
      }
  </style>
  """))

  # 지도에서 특정 지역을 클릭했을 때 해당 지역의 이름이 들어간 url로 바뀜
  test = folium.utilities.JsCode("""
  function(feature, layer) {
      layer.on('click', function(e) {
          let area = feature.properties.CTP_KOR_NM;
          if (area) {
              window.parent.location.href = '/domestic/' + encodeURIComponent(area);
          }
      });
  }
  """)


  
  # GeoJson에서 툴팁 기능 추가
  folium.GeoJson(
    geo_str,
    name='지역별 데이터',
    style_function=lambda feature: {
        'weight': 0.1,
        'color': 'transparent',
    },
    highlight_function=lambda feature: {
        'weight': 1,
        'fillOpacity': 0.4,
        'color': 'transparent',
    },
    popup=None,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['CTP_KOR_NM', 'confirmed', 'deaths'],  # 표시할 데이터
        aliases=['지역 이름:', '누적 확진자:', '누적 사망자:'],  # 레이블
        localize=True,
        labels=True,
        sticky=True
    ),
    onEachFeature = test
  ).add_to(map)
    
  map_html = map._repr_html_()

  return render_template('domestic/index.html', map_html = map_html , articles = articles)



@bp.route('/<string:area>')
def region(area):
  # 코로나 기사 크롤링
  articles = common_data(area)

  # 해당 지역과 관련된 코로나 발생률과 사망률 데이터 뽑아옴.
  area_data = sheet_data.get('시군구별(발생률,사망률)')
  
  filtered_data = area_data.query('시도명 == @area')
  filtered_total = filtered_data.query("시군구!='합계'")
  try: 
    area_info = {area: filtered_total.to_dict(orient='records')}
  except KeyError:
    return f"{area} 데이터가 없습니다.", 404
  
  
  # 지역 이름 변환 규칙
  if area in ["충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도"]:
      short_area = area[0] + area[2]  # 첫 번째 글자 + 세 번째 글자
  else:
      short_area = area[:2]  # 앞 두 글자만 가져오기
  
  api_key = 'dacNztaQsUeSWz3VaWB%2B1d%2FgvQyr5brzFt9uq5%2B3au2oEmoCdzkWXPehjRwi5R4pdN%2F%2Fjeyklm4ZJDoHfoXLPg%3D%3D'
  
  url = f"http://apis.data.go.kr/1352000/ODMS_COVID_06/callCovid06Api?serviceKey={api_key}&sido={short_area}"
  response = requests.get(url)
  data = xmltodict.parse(response.text)
  try:
    items = data['response']['body']['items']['item']
    if not isinstance(items,list):
      items = [items]

    hospitals = [
      {'name': item.get('hospitalNm'), 'address': item.get('hospitalAddr'), 'tel': item.get('hospitalTel'), 'sido': item.get('sido')}
      for item in items
    ]
    print(hospitals)

  except KeyError:
    return f"{area}에 대한 데이터를 찾을 수 없습니다.", 404

  return render_template('domestic/index.html', area=area, area_info=area_info, articles=articles)