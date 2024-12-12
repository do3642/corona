from flask import Blueprint, jsonify
import os
import pandas as pd

bp = Blueprint('data', __name__)

# 엑셀 데이터 불러옴.
path = os.path.join('apps','static','data','국내_코로나_발생_현황.xlsx')
covid_data = pd.read_excel(path, sheet_name=None)

p_path = os.path.join('apps','static', 'data', '연령별_인구수.xlsx')
population_data = pd.read_excel(p_path)

# 엑셀에 있는 시트들이 딕셔너리 안에 하나씩 들어감.
sheet_data = { sheet : data for sheet, data in covid_data.items() }

@bp.route('/<graph_id>', methods=['GET'])
def get_graph(graph_id):
  if graph_id == 'area_incidence':
    area = sheet_data.get('시군구별(발생률,사망률)')
    area_total = area.query("시군구=='합계'")
    data = {
      "labels": area_total['시도명'].tolist(),
      "values": area_total['발생률\n(인구10만명당, 명)'].tolist(),
      "label": '지역별 코로나 발생률(인구 10만명당, 명)',
      "type": "bar",
      "backgroundColor": "rgba(101,148,189,1)"
    }
    return jsonify(data)
  
  elif graph_id == 'area_death':
    area = sheet_data.get('시군구별(발생률,사망률)')
    area_total = area.query("시군구=='합계'")
    data = {
      'labels': area_total['시도명'].tolist(),
      'values': area_total['사망률\n(인구10만명당, 명)'].tolist(),
      'label': '지역별 코로나 사망률(인구 10만명당, 명)',
      'type': 'bar',
      'backgroundColor': 'rgba(189,101,101,1)'
    }

    return jsonify(data)
  
  elif graph_id == 'age_incidence':
    age = sheet_data.get('연령별(10세단위)')
    cumulative_cases = age.iloc[0, 2:]
    cumulative_cases.index = age.columns[2:]

    average_population = population_data.iloc[:, 2:].mean()
    print(average_population)

    incidence_rate = (cumulative_cases / average_population) * 100

    print(incidence_rate.isnull())

    data = {
      "labels": incidence_rate.index.tolist(),
      "values": incidence_rate.tolist(),
      "label": '연령대별 코로나 발생률(%)',
      "type": "bar",
      "backgroundColor": 'rgba(202, 190, 28, 1)'
    }

    return jsonify(data)
    
  
  else:
    return jsonify({"error": "해당 그래프ID는 존재하지 않는 그래프입니다."}), 404