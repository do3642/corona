from flask import Blueprint, render_template,jsonify
import folium
import folium.features
import folium.utilities
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

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
  print(table_data)
  # 데이터를 JSON 형태로 반환
  return jsonify(table_data)

@bp.route('/<string:area>')
def region(area):
  # 해당 지역과 관련된 코로나 발생률과 사망률 데이터 뽑아옴.
  area_data = sheet_data.get('시군구별(발생률,사망률)')
  
  filtered_data = area_data.query('시도명 == @area')
  filtered_total = filtered_data.query("시군구!='합계'")
  try: 
    area_info = {area: filtered_total.to_dict(orient='records')}
    print(area_info)
  except KeyError:
    return f"{area} 데이터가 없습니다.", 404
  
  return render_template('domestic/area_index.html', area=area, area_info=area_info)

