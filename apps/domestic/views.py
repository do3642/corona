from flask import Blueprint, render_template
import folium
import os
import pandas as pd
import matplotlib.pyplot as plt

bp = Blueprint(
  "domestic",
  __name__,
  template_folder="templates",
  static_folder="static"
  )

# 국내 코로나 현황 데이터 불러옴.
path = os.path.join('apps', 'static', 'data', '국내_코로나_발생_현황.xlsx')
covid_data = pd.read_excel(path, sheet_name=None)

for sheet,a in covid_data.items():
  print(f'이름 : {sheet}')
  print(a)

@bp.route('/')
def index():
  # 지도가 전국이 다 보일 수 있도록 설정.
  map = folium.Map( location=[36, 128.00025], zoom_start=7.25, tiles="CartoDB positron")

  map_html = map._repr_html_()
  print(covid_data.head)
  return render_template('domestic/index.html', map_html = map_html)