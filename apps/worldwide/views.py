from flask import Blueprint, render_template, jsonify,request
import datetime

from apps.worldwide.covid_utils import get_covid_data_for_date, get_covid_map_and_data, fetch_data_by_period
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
    daily_classList = [
        {'label': '확진자', 'className': 'new-cases'},
        {'label': '완치자', 'className': 'new-recoveries'},
        {'label': '사망자', 'className': 'new-deaths'}
    ]
    total_classList = [
        {'className': 'total-cases'},
        {'className': 'total-recoveries'},
        {'className': 'total-deaths'}
    ]
    
    return render_template(
        'worldwide/worldwide_data.html',
        records=records,
        country_percentages=country_percentages,
        daily_classList = daily_classList,
        total_classList = total_classList
    )

@worldwide_bp.route('/data', methods=['GET'])
def worldwide_data_json():
    selected_date = request.args.get('date', datetime.datetime.now().date() - datetime.timedelta(days=365 * 2 + 180))
    if isinstance(selected_date, str):
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()

    records, country_percentages, _ = get_covid_map_and_data(selected_date)

    return jsonify({
        'records': [
            {
                'country': record[0].country,
                'country_korean': record[1].country_korean,
                'new_cases': record[0].new_cases,
                'new_deaths': record[0].new_deaths,
                'cumulative_cases': record[0].cumulative_cases,
                'cumulative_deaths': record[0].cumulative_deaths,
                'lat': record[2].country_lat,
                'lng': record[2].country_long,
            }
            for record in records
        ],
        'country_percentages': country_percentages,
        'date_reported': records[0][0].date_reported.strftime('%Y-%m-%d') if records else None
    })


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
    if not country:
        return jsonify({"error": "Country parameter is required"}), 400

    try:
        # 일간, 주간, 월간 데이터 조회
        daily_data = fetch_data_by_period(country, 'daily')
        weekly_data = fetch_data_by_period(country, 'weekly')
        monthly_data = fetch_data_by_period(country, 'monthly')

        # 모든 데이터를 합쳐서 반환
        response_data = {
            "daily": daily_data,
            "weekly": weekly_data,
            "monthly": monthly_data
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500




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
