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
  # 지역별 코로나 발병률(명)
  if graph_id == 'area_incidence':
    area = sheet_data.get('시군구별(발생률,사망률)')
    area_total = area.query("시군구=='합계'")
    data = {
      "labels": area_total['시도명'].tolist(),
      "values": area_total['발생률\n(인구10만명당, 명)'].tolist(),
      "label": '지역별 코로나 발병률(인구 10만명당, 명)',
      "type": "bar",
      "backgroundColor": "rgba(101,148,189,1)"
    }
    return jsonify(data)
  
  # 지역별 코로나로 인한 사망률(명)
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
  
  # 연령별 전체 인구 중 코로나 발병률(%)
  elif graph_id == 'age_incidence':
    age = sheet_data.get('연령별(10세단위)')
    cumulative_cases = age.iloc[0, 2:]
    cumulative_cases.index = age.columns[2:]

    average_population = population_data.iloc[:, 2:].mean()

    incidence_rate = (cumulative_cases / average_population) * 100

    data = {
      "labels": incidence_rate.index.tolist(),
      "values": incidence_rate.tolist(),
      "label": '연령대별 코로나 발병률(%)',
      "type": "bar",
      "backgroundColor": 'rgba(202, 190, 28, 1)'
    }

    return jsonify(data)
  
  # 연령별 전체 인구 중 코로나로 인한 사망률(%)
  elif graph_id == 'age_death':
    age = sheet_data.get('연령별사망(10세단위)')
    cumulative_deaths = age.iloc[0, 2:]
    cumulative_deaths.index = age.columns[2:]

    average_population = population_data.iloc[:, 2:].mean()

    death_rate = (cumulative_deaths / average_population) * 100

    data = {
      "labels": death_rate.index.tolist(),
      "values": death_rate.tolist(),
      "label": '연령대별 코로나 사망률(%)',
      "type": "bar",
      "backgroundColor": 'rgba(187, 100, 68, 1)'
    }

    return jsonify(data)

  # 연령별 코로나 확진자 중 사망률(%)
  elif graph_id == 'case_death_rate':
    age = sheet_data.get('연령별(10세단위)')
    cumulative_cases = age.iloc[0, 2:]
    cumulative_cases.index = age.columns[2:]

    age_death = sheet_data.get('연령별사망(10세단위)')
    cumulative_deaths = age_death.iloc[0, 2:]
    cumulative_deaths.index = age_death.columns[2:]

    case_death = (cumulative_deaths / cumulative_cases) * 100

    data = {
      "labels": case_death.index.tolist(),
      "values": case_death.tolist(),
      "label" : '확진자 중 사망률(%)',
      "type": 'bar',
      "backgroundColor": 'rgba(211, 49, 49, 1)'
    }

    return jsonify(data)
  
  # 지역별 시간에 따른 코로나 확진자 수
  # elif graph_id == 'time_incidence':
  #   df = sheet_data.get('시도별발생(17개시도+검역)')
  #   time = df.query("일자 != '누적(명)'")

  #   return jsonify(data)
  
  else:
    return jsonify({"error": "해당 그래프ID는 존재하지 않는 그래프입니다."}), 404