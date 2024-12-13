from flask import Blueprint, render_template, jsonify,request
import datetime

from apps.worldwide.covid_utils import get_covid_data_for_date, get_covid_map_and_data
from apps.worldwide.insertData import insert_data_to_db
from apps.worldwide.insertCountryTranslations import insert_country_translations
from apps.worldwide.insertLatLong import insert_data_to_db_Lat_Long
from apps.worldwide.models import WhoData, CountryTranslation,WorldLatLong
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
    records, country_percentages, _ = get_covid_map_and_data()
    return render_template(
        'worldwide/worldwide_data.html',
        records=records,
        country_percentages=country_percentages,

    )
@worldwide_bp.route('/request/marker-data')
def api_marker_data():
    _, _,  marker_data = get_covid_map_and_data()  # marker_data만 반환
    return jsonify(marker_data)

# 전세계 데이터 계산 후 리턴
@worldwide_bp.route('/covid-data/<date_type>', methods=['GET'])
def get_covid_data(date_type):
    try:
        data = get_covid_data_for_date(date_type)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 그래프 요청 라우터


@worldwide_bp.route('/get-daily-data', methods=['GET'])
def get_daily_data():
    country = request.args.get('country')  # URL 쿼리 파라미터에서 'country' 값을 가져옴
    print(country)
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)

    # 데이터 조회
    data = db.session.query(
        WhoData.new_cases,
        WhoData.new_recoveries,
        WhoData.new_deaths
    ).filter(
        WhoData.date_reported == two_years_ago, 
        WhoData.country == country
    ).first()
    
    print(data)

    # Row 객체를 딕셔너리로 변환
    if data:
        data_dict = {
            "new_cases": data.new_cases,
            "new_recoveries": data.new_recoveries,
            "new_deaths": data.new_deaths
        }
    else:
        data_dict = {
            "new_cases": 0,
            "new_recoveries": 0,
            "new_deaths": 0
        }
    print(data_dict)

    return jsonify(data_dict)  # JSON 형태로 응답 반환


# 데이터 삽입 라우트
@worldwide_bp.route('/insert-data')
def insert_data():
    insert_data_to_db()
    return "데이터 삽입 작업이 완료되었습니다!"

@worldwide_bp.route('/insert-trans-data')
def insert_trans_data():
    insert_country_translations()
    return "번역 작업 완료"

@worldwide_bp.route('/insert-latlong-data')
def insert_LatLong_data():
    insert_data_to_db_Lat_Long()
    return "위,경도 데이터 삽입 작업이 완료되었습니다!"
