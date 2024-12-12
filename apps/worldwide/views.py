from flask import Blueprint, render_template, jsonify
from apps.worldwide.covid_utils import get_covid_data_for_date, get_covid_map_and_data
from apps.worldwide.insertData import insert_data_to_db
from apps.worldwide.insertCountryTranslations import insert_country_translations
from apps.worldwide.insertLatLong import insert_data_to_db_Lat_Long

worldwide_bp = Blueprint(
    'worldwide',
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix='/worldwide'
)

@worldwide_bp.route('/')
def worldwide_data():
    records, country_percentages, map_html, _ = get_covid_map_and_data()
    return render_template(
        'worldwide/worldwide_data.html',
        map_html=map_html,
        records=records,
        country_percentages=country_percentages,

    )
@worldwide_bp.route('/request/marker-data')
def api_marker_data():
    _, _, _, marker_data = get_covid_map_and_data()  # marker_data만 반환
    return jsonify(marker_data)

@worldwide_bp.route('/covid-data/<date_type>', methods=['GET'])
def get_covid_data(date_type):
    try:
        data = get_covid_data_for_date(date_type)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@worldwide_bp.route('/insert-latlong-data')
def insert_LatLong_data():
    insert_data_to_db_Lat_Long()
    return "위,경도 데이터 삽입 작업이 완료되었습니다!"
