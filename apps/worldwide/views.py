from flask import Blueprint, render_template

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