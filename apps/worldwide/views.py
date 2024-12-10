from flask import Blueprint, render_template

import datetime
import folium

from apps.worldwide.insertData import insert_data_to_db
from apps.worldwide.models import WhoData
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

    # 현재날짜
    current_date = datetime.datetime.now().date()
    # 데이터 업데이트가 안되므로 임의의 날짜를 잡기위해 현재 날짜 -2년6개월
    two_years_ago = current_date - datetime.timedelta(days=365*2-180)

    # 날짜레코드중 현재날짜-2년6개월한 날짜와 같을때 country컬럼의 중복값을 제거한 레코드들을 담음
    records = WhoData.query.filter(WhoData.date_reported == two_years_ago).distinct(WhoData.country).all()




     # Folium 지도 생성
    start_coords = [20, 0]  # 전 세계 중심 좌표
    world_map = folium.Map(location=start_coords, zoom_start=2)

    # 마커 추가
    folium.Marker([37.5665, 126.9780], popup='Seoul, South Korea').add_to(world_map)  # 서울
    folium.Marker([40.7128, -74.0060], popup='New York, USA').add_to(world_map)      # 뉴욕
    folium.Marker([48.8566, 2.3522], popup='Paris, France').add_to(world_map)        # 파리

    # 지도 HTML을 문자열로 변환

    map_html = world_map._repr_html_()

    return render_template('worldwide/worldwide_data.html', map_html=map_html, records=records)

# 데이터 삽입 라우트
@worldwide_bp.route('/insert-data')
def insert_data():
    insert_data_to_db()
    return "데이터 삽입 작업이 완료되었습니다!"