from datetime import timedelta
import datetime
import folium
from folium.plugins import MarkerCluster
import json
import os


from apps.worldwide.models import WhoData, CountryTranslation,WorldLatLong
from apps.app import db


def get_covid_data_for_date(date_type):
    # 데이터 타입은 셀렉트 박스에서 클릭한 value
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)
    
    # 2년6개월 전을 오늘로 기본세팅
    today = two_years_ago
    if date_type == "yesterday":
        date = today - timedelta(days=1)
    elif date_type == "tomorrow":
        date = today + timedelta(days=1)
    else:  
        date = today

    # 해당 날짜에 해당하는 전체확진자,전체사망자 뽑아옴
    # 한번에 두개 다 뽑는 이유는
    # 어제 ,오늘 ,내일 선택하는 카테고리가 있는데 그거에 맞게끔 전날과 비교해서 증가,감소량을 파악하기 위함
    covid_data_today = db.session.query(
        db.func.sum(WhoData.new_cases).label('total_new_cases_today'),
        db.func.sum(WhoData.new_deaths).label('total_new_deaths_today')
    ).filter(WhoData.date_reported == date).first()

    yesterday = date - timedelta(days=1)
    covid_data_yesterday = db.session.query(
        db.func.sum(WhoData.new_cases).label('total_new_cases_yesterday'),
        db.func.sum(WhoData.new_deaths).label('total_new_deaths_yesterday')
    ).filter(WhoData.date_reported == yesterday).first()

    if not covid_data_today:
        return {"error": "No data found for the selected date."}, 404

    # 데이터가 튜플형태로 담겨있어서 따로 분리시켜줌 값이없으면 0 예외처리
    total_new_cases_today = covid_data_today.total_new_cases_today or 0
    total_new_deaths_today = covid_data_today.total_new_deaths_today or 0
    total_new_cases_yesterday = covid_data_yesterday.total_new_cases_yesterday or 0
    total_new_deaths_yesterday = covid_data_yesterday.total_new_deaths_yesterday or 0

    # 전날과 오늘을 비교하여 증가,감소량 계산
    new_cases_change = total_new_cases_today - total_new_cases_yesterday
    new_deaths_change = total_new_deaths_today - total_new_deaths_yesterday

    # 해당하는 날짜의 모든 국가들이 가지고 있는 누적확진자를 합산함 (전세계 누적 확진자,사망자)
    # scalar을 쓰는 이유는 안쓰면 튜플에 있는값을 한번 더 꺼내야함
    total_cases = db.session.query(
        db.func.sum(WhoData.cumulative_cases).label('total_cumulative_cases')
    ).filter(WhoData.date_reported == date).scalar()

    total_deaths = db.session.query(
        db.func.sum(WhoData.cumulative_deaths).label('total_cumulative_deaths')
    ).filter(WhoData.date_reported == date).scalar()

    # 완치자는 데이터 세팅이 안돼서 기본 0
    total_recovered = 0

    # 딕셔너리 형태 키/밸류로 반환
    return {
        "new_cases": total_new_cases_today,
        "new_cases_change": new_cases_change,
        "new_deaths": total_new_deaths_today,
        "new_deaths_change": new_deaths_change,
        "total_cases": total_cases,
        "total_cases_change": total_new_cases_today,
        "total_recovered": total_recovered,
        "total_recovered_change": 0,
        "total_deaths": total_deaths,
        "total_deaths_change": total_new_deaths_today
    }




def get_covid_map_and_data():
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)

    records = db.session.query(WhoData, CountryTranslation, WorldLatLong).filter(
        WhoData.date_reported == two_years_ago,
        WhoData.country_code == CountryTranslation.country_code,
        WhoData.country_code == WorldLatLong.country_code
    ).distinct(WhoData.country).all()

    total_new_cases = sum(record[0].new_cases for record in records)

    country_percentages = []
    for record in records:
        who_data = record[0]
        country_translation = record[1]

        if total_new_cases > 0:
            percentage = (who_data.new_cases / total_new_cases) * 100
            country_percentages.append({
                'country': who_data.country,
                'country_korean': country_translation.country_korean,
                'percentage': round(percentage, 2)
            })


     # 마커 데이터 생성
    marker_data = []
    for record in records:
        lat = record[2].country_lat
        lng = record[2].country_long
        country = record[0].country
        marker_data.append({
            'lat': lat,
            'lng': lng,
            'country': country
        })

    # 폴리움 지도 생성
    start_coords = [20, 0]
    world_map = folium.Map(location=start_coords, zoom_start=2)

    marker_cluster = MarkerCluster().add_to(world_map)

    for marker in marker_data:
        folium.Marker(
            [marker['lat'], marker['lng']],
            popup=f"{marker['country']}"
        ).add_to(marker_cluster)

    geojson_file = os.path.join(os.path.dirname(__file__), 'static/data/world_countries.json')
    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    folium.GeoJson(
        geojson_data,
        name='geojson'
    ).add_to(marker_cluster)

    map_html = world_map._repr_html_()

    return records, country_percentages, map_html, marker_data