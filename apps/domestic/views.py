from flask import Blueprint, render_template
import folium

bp = Blueprint(
  "domestic",
  __name__,
  template_folder="templates",
  static_folder="static"
  )

@bp.route('/')
def index():
  # 지도가 전국이 다 보일 수 있도록 설정.
  map = folium.Map( location=[36, 128.00025], zoom_start=7.25, tiles="CartoDB positron")
  
  map_html = map._repr_html_()

  return render_template('domestic/index.html', map_html = map_html)