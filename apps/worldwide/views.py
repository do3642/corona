from flask import Blueprint, render_template
import folium
from io import BytesIO

worldwide_bp = Blueprint(
    'worldwide',
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix='/worldwide'
    )

@worldwide_bp.route('/')
def worldwide_data():
     # Folium 지도 생성
    start_coords = [20, 0]  # 전 세계 중심 좌표
    world_map = folium.Map(location=start_coords, zoom_start=2)

    # 마커 추가
    folium.Marker([37.5665, 126.9780], popup='Seoul, South Korea').add_to(world_map)  # 서울
    folium.Marker([40.7128, -74.0060], popup='New York, USA').add_to(world_map)      # 뉴욕
    folium.Marker([48.8566, 2.3522], popup='Paris, France').add_to(world_map)        # 파리

    # 지도 HTML을 문자열로 변환

    map_html = world_map._repr_html_()

    return render_template('worldwide/worldwide_data.html', map_html=map_html)