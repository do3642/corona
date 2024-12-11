from flask import Blueprint, jsonify
import os
import pandas as pd

bp = Blueprint('data', __name__)

# 엑셀 데이터 불러옴.
path = os.path.join('apps','static','data','국내_코로나_발생_현황.xlsx')
covid_data = pd.read_excel(path, sheet_name=None)

# 엑셀에 있는 시트들이 딕셔너리 안에 하나씩 들어감.
sheet_data = { sheet : data for sheet, data in covid_data.items() }

@bp.route('/area_incidence', methods=['GET'])
def get_area_incidence():
  area = sheet_data.get('시군구별(발생률,사망률)')
  area_total = area.query("시군구=='합계'")
  data = {
    "labels": area_total['시도명'].tolist(),
    "values": area_total['발생률\n(인구10만명당, 명)'].tolist(),
    "label": '지역별 코로나 발생률(23.8.31 0시기준(인구 10만명당, 명))',
    "type": 'line',
    "borderColor": 'rgba(101,148,189,1)'
  }

  return jsonify(data)