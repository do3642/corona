from flask import Blueprint, render_template, request, jsonify
import folium
import folium.features
import folium.utilities
import requests
from bs4 import BeautifulSoup
import json
import xmltodict
import pandas as pd
import os

from apps.domestic.data import sheet_data

bp = Blueprint(
  "domestic",
  __name__,
  template_folder="templates",
  static_folder="static"
  )

# JSON 파일에서 지역별 중심 좌표 로드
with open('apps/static/data/center_coords.json', 'r', encoding='utf-8') as f:
  center_coords = json.load(f)
  

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
              window.parent.location.href = '/' + encodeURIComponent(area);
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

@bp.route('/api/covid-summary', methods=['GET'])
def get_covid_summary():
   # CSV 파일 경로 설정
  csv_path = os.path.join(os.getcwd(), 'apps/static/data/코로나격리해제.csv')

  # CSV 파일 읽기
  data = pd.read_csv(csv_path)

  # "검역" 값을 제외
  data = data[data["region"] != "검역"]

  # 제공된 데이터프레임 형태로 변환
  # 그룹화하여 지역별로 합계 계산
  df = data.groupby("region").agg(
      확진자=("confirmed", "sum"),
      사망자=("death", "sum"),
      격리해제=("released", "sum"),
  ).reset_index()

  # 열 이름 변환
  df.columns = ["지역", "확진자", "사망자", "격리해제"]
  df = df.copy()
  df["완치율(%)"] = (df["격리해제"] / df["확진자"] * 100).round(2)
  df["완치율(%)"] = df["완치율(%)"].fillna("N/A")  # 결측값 처리

  table_data = df.to_dict(orient="records")  # 데이터를 딕셔너리 리스트로 변환
   # 데이터를 딕셔너리 리스트로 변환
  table_data = df.to_dict(orient="records")
  
  # 데이터를 JSON 형태로 반환
  return jsonify(table_data)

@bp.route('/<string:area>')
def region(area):
  # 코로나 기사 크롤링
  articles = common_data(area)

  # 해당 지역과 관련된 코로나 발생률과 사망률 데이터 뽑아옴.
  area_data = sheet_data.get('시군구별(발생률,사망률)')
  filtered_data = area_data.query('시도명 == @area')
  filtered_total = filtered_data.query("시군구!='합계'")
  
  if filtered_total.empty:
    return f"{area} 데이터가 없습니다.", 404
  
  area_info = {area: filtered_total.to_dict(orient='records')}

  # 지역 중심 좌표 데이터 가져오기
  with open('apps/static/data/center_coords.json', 'r', encoding='utf-8') as f:
    center_coords = json.load(f)

  region_center = center_coords.get(area)
  if not region_center:
    region_center = [35.75, 128.00025]

  # 지도를 해당 지역으로 줌인
  map = folium.Map(location=region_center, zoom_start=9)

  geojson_path = 'apps/static/data/korea.json'

  with open(geojson_path, 'r', encoding='utf-8') as f:
    geo_json_data = json.load(f)

  geojson = folium.GeoJson(geo_json_data)

  # 현재 지역만 필터링하여 GeoJSON 데이터 추출
  target_feature = None
  for feature in geo_json_data['features']:
    if feature['properties']['CTP_KOR_NM'] == area:
      target_feature = feature
      break

  if target_feature:
    geojson = folium.GeoJson({
      'type': 'FeatureCollection',
      'features': [target_feature]
    })
  else:
    geojson = folium.GeoJson({
      'type': 'FeatureCollection',
      'features': []
    })

  # GeoJson에서 툴팁 기능과 강조 스타일 추가
  folium.GeoJson(
      geo_json_data,
      name='지역별 데이터',
      highlight_function=None,
      style_function=lambda feature: {
          'weight': 0.1,
          'color': 'transparent',
      },
      popup=None
  ).add_to(map)

  # 특정 지역을 자동으로 강조하는 JavaScript 코드 추가
  if area:  # 지역이 존재하면
      highlight_js = f"""
      var targetArea = "{area}";  // 자동 강조할 지역 이름
      var geojsonLayer = {geojson._name};
      geojsonLayer.eachLayer(function(layer) {{
          if (layer.feature.properties.CTP_KOR_NM === targetArea) {{
              layer.setStyle({{
                  weight: 10,
                  color: 'orange',
                  fillOpacity: 0.4,
              }});
              layer.bringToFront();
          }}
      }});
      """
      map.get_root().html.add_child(folium.Element(f"<script>{highlight_js}</script>"))

  geojson.add_to(map)

  map_html = map._repr_html_()


  # 줄임말로 시도명이 이루어진 api에서 맞는 데이터를 가져오기 위해 지역 이름 변환
  if area in ["충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도"]:
    short_area = area[0] + area[2]
  else:
    short_area = area[:2]

  # 병원 데이터 API 호출
  api_key = 'dacNztaQsUeSWz3VaWB%2B1d%2FgvQyr5brzFt9uq5%2B3au2oEmoCdzkWXPehjRwi5R4pdN%2F%2Fjeyklm4ZJDoHfoXLPg%3D%3D'
  url = f"http://apis.data.go.kr/1352000/ODMS_COVID_06/callCovid06Api?serviceKey={api_key}&sido={short_area}"
  response = requests.get(url)
  data = xmltodict.parse(response.text)

  try:
    items = data['response']['body']['items']['item']
    if not isinstance(items, list):
      items = [items]

    hospitals = [
      {'name': item.get('hospitalNm'), 'tel': item.get('hospitalTel'), 'url': f"https://map.naver.com/p/search/{item.get('hospitalNm')}"}
       for item in items
    ]

  except KeyError:
    hospitals = []

  # 페이지네이션 관련 계산
  page1 = request.args.get('page1', type=int, default=1)
  page2 = request.args.get('page2', type=int, default=1)

  per_page = 10
  block_size = 3

  # 지역 데이터 표 페이지네이션
  offset = (page1 - 1) * per_page
  area_paging_items = area_info[area][offset:offset + per_page]

  area_total_pages = (len(area_info[area]) + per_page - 1) // per_page
  area_group_start = ((page1 - 1) // block_size) * block_size + 1
  area_group_end = min(area_group_start + block_size - 1, area_total_pages)

  # 병원 데이터 표 페이지네이션
  offset2 = (page2 - 1) * per_page
  hospital_paging_items = hospitals[offset2:offset2 + per_page]

  hospital_total_pages = (len(hospitals) + per_page - 1) // per_page
  hospital_group_start = ((page2 - 1) // block_size) * block_size + 1
  hospital_group_end = min(hospital_group_start + block_size - 1, hospital_total_pages)

  return render_template(
    'domestic/index.html', 
    map_html=map_html,
    area=area, area_info=area_info, 
    articles=articles, 
    hospitals=hospitals,
    page1=page1,
    page2=page2,
    area_paginated=area_paging_items,
    hospital_paginated=hospital_paging_items,
    area_group_start=area_group_start,
    area_group_end=area_group_end,
    area_prev_block=area_group_start > 1,
    area_next_block=area_group_end < area_total_pages,
    hospital_group_start=hospital_group_start,
    hospital_group_end=hospital_group_end,
    hospital_prev_block=hospital_group_start > 1,
    hospital_next_block=hospital_group_end < hospital_total_pages
    )
