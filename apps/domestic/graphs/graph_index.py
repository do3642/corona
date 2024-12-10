import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

import matplotlib
matplotlib.use('Agg')

# 엑셀 데이터 불러옴.
path = os.path.join('apps', 'static', 'data', '국내_코로나_발생_현황.xlsx')
covid_data = pd.read_excel(path, sheet_name=None)

# 엑셀에 있는 시트들이 딕셔너리 안에 하나씩 들어감.
sheet_data = { sheet : data for sheet, data in covid_data.items() }

def generate_garph(graph_id, sheet_data):
  if graph_id == 'area_incidence':
    # 데이터 가공
    area = sheet_data.get('시군구별(발생률,사망률)')
    area_total = area.query("시군구=='합계'")

    # 그래프1 생성
    plt.rc('font', family='malgun gothic')
    plt.plot(area_total['시도명'], area_total['발생률\n(인구10만명당, 명)'], color='blue', linestyle='-', marker='o')
    plt.xlabel('시도명')
    plt.ylabel('발생률(인구 10만명당, 명)')
    plt.title('지역별 코로나 발생률(23.8.31 0시 기준)')
  
  elif graph_id == 'area_death':
    area = sheet_data.get('시군구별(발생률, 사망률)')
    area_total = area.query("시군구=='합계'")

    # 그래프2 생성
    plt.rc('font', family='malgun gothic')
    plt.plot(area_total['시도명'], area_total['발생률\n(인구10만명당, 명)'], color='red', linestyle='-', marker='o')
    plt.xlabel('시도명')
    plt.ylabel('사망률(인구 10만명당, 명)')
    plt.title('지역별 코로나 사망률(23.8.31 0시 기준)')

  else:
    return None

  img = BytesIO()
  plt.savefig(img, format='png', dpi=200)
  img.seek(0)
  graph_base64 = base64.b64encode(img.read()).decode('utf-8')

  plt.close()

  return graph_base64