from flask import Blueprint, render_template,jsonify
from datetime import timedelta
import datetime
import folium

from apps.worldwide.insertData import insert_data_to_db
from apps.worldwide.insertCountryTranslations import insert_country_translations
from apps.worldwide.models import WhoData, CountryTranslation
from apps.app import db

worldwide_bp = Blueprint(
    'worldwide',
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix='/worldwide'
    )

@worldwide_bp.route('/')
def worldwide_data():

    # -------------------임의의 데이터 업데이트 날짜를 표기 (해당 날짜 기준으로 일일 감염률 표기) ---------------
    # 현재 날짜
    current_date = datetime.datetime.now().date()
    # 데이터 업데이트가 안되므로 임의의 날짜를 잡기 위해 현재 날짜 -2년 6개월
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 - 180)

    # 날짜 레코드 중 현재 날짜 - 2년 6개월 한 날짜와 같을 때 country 컬럼의 중복값을 제거한 레코드들을 담음
    # WhoData와 CountryTranslation을 JOIN (번역 테이블 조인)
    records = db.session.query(WhoData, CountryTranslation).filter(
        WhoData.date_reported == two_years_ago,
        WhoData.country_code == CountryTranslation.country_code
    ).distinct(WhoData.country).all()
    
    # -------------------일일 감염률을 위한 계산 ---------------
    # 전체 new_cases 합산
    total_new_cases = sum(record[0].new_cases for record in records)

    # 각 country의 new_cases 비율 계산
    country_percentages = []
    for record in records:
        who_data = record[0]
        country_translation = record[1]

        if total_new_cases > 0:  # total_new_cases가 0일 경우 방지
            percentage = (who_data.new_cases / total_new_cases) * 100
            country_percentages.append({
                'country': who_data.country,  # 영어 국가명
                'country_korean': country_translation.country_korean,  # 한글 국가명
                'percentage': round(percentage, 2)  # 소수점 2자리까지 표시
            })

    # -------------------Folium 지도 생성 ---------------
    start_coords = [20, 0]  # 전 세계 중심 좌표
    world_map = folium.Map(location=start_coords, zoom_start=2)

    # 예제 마커 추가
    folium.Marker([37.5665, 126.9780], popup='Seoul, South Korea').add_to(world_map)  # 서울
    folium.Marker([40.7128, -74.0060], popup='New York, USA').add_to(world_map)      # 뉴욕
    folium.Marker([48.8566, 2.3522], popup='Paris, France').add_to(world_map)        # 파리

    # 지도 HTML을 문자열로 변환
    map_html = world_map._repr_html_()

    # -------------------결과 렌더링 ---------------
    return render_template(
        'worldwide/worldwide_data.html',
        map_html=map_html,
        records=records,
        country_percentages=country_percentages
    )

# 데이터 삽입 라우트
@worldwide_bp.route('/insert-data')
def insert_data():
    insert_data_to_db()
    insert_country_translations()
    return "데이터 삽입 작업이 완료되었습니다!"


@worldwide_bp.route('/insert-trans-data')
def insert_trans_data():
    insert_country_translations()
    return "번역 작업 완료"


def get_covid_data_for_date(date_type):
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 - 180)

    today = two_years_ago
    if date_type == "yesterday":
        date = today - timedelta(days=1)
    elif date_type == "tomorrow":
        date = today + timedelta(days=1)
    else:  # "today"
        date = today

    # 해당 날짜에 해당하는 확진자,사망자의 합
    covid_data_today = db.session.query(
        db.func.sum(WhoData.new_cases).label('total_new_cases_today'),
        db.func.sum(WhoData.new_deaths).label('total_new_deaths_today')
    ).filter(WhoData.date_reported == date).first()
    # 해당 날짜의 어제에 해당하는 확진자,사망자의 합
    yesterday = date - timedelta(days=1)
    covid_data_yesterday = db.session.query(
        db.func.sum(WhoData.new_cases).label('total_new_cases_yesterday'),
        db.func.sum(WhoData.new_deaths).label('total_new_deaths_yesterday')
    ).filter(WhoData.date_reported == yesterday).first()

    # 값이 없으면 오류코드와 404페이지 반환
    if not covid_data_today:
        return {"error": "No data found for the selected date."}, 404

    # 오늘과 어제의 신규 확진자 수, 신규 사망자 수 //튜플형태를 분리
    total_new_cases_today = covid_data_today.total_new_cases_today or 0
    total_new_deaths_today = covid_data_today.total_new_deaths_today or 0
    total_new_cases_yesterday = covid_data_yesterday.total_new_cases_yesterday or 0
    total_new_deaths_yesterday = covid_data_yesterday.total_new_deaths_yesterday or 0


    # 신규 확진자 변화량 (오늘 - 어제)
    new_cases_change = total_new_cases_today - total_new_cases_yesterday
    new_deaths_change = total_new_deaths_today - total_new_deaths_yesterday
  

    # -------------------누적 확진자 수 (전체 확진자) 계산-------------------
    total_cases = db.session.query(
        db.func.sum(WhoData.cumulative_cases).label('total_cumulative_cases')
    ) \
    .filter(WhoData.date_reported == date) \
    .scalar() 


    # 전체 누적 사망자 수 계산
    total_deaths = db.session.query(
        db.func.sum(WhoData.cumulative_deaths).label('total_cumulative_deaths')
    ) \
    .filter(WhoData.date_reported == date) \
    .scalar()

    # 전체 회복자 수는 아직 없으므로 0으로 설정
    total_recovered = 0

    
    


    # -------------------결과 반환-------------------
    return {
        "new_cases": total_new_cases_today,
        "new_cases_change": new_cases_change,
        "new_deaths": total_new_deaths_today,
        "new_deaths_change":new_deaths_change,
        "total_cases": total_cases,  
        "total_cases_change": total_new_cases_today,
        "total_recovered": total_recovered,
        "total_recovered_change": 0, 
        "total_deaths": total_deaths, 
        "total_deaths_change": total_new_deaths_today 
    }


@worldwide_bp.route('/covid-data/<date_type>', methods=['GET'])
def get_covid_data(date_type):
    try:
        data = get_covid_data_for_date(date_type)
        return jsonify(data)
    except Exception as e:
        # 오류가 발생한 경우 500 오류와 함께 메시지 반환
        return jsonify({"error": str(e)}), 500
