from flask import Blueprint, render_template, jsonify
import folium
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from apps.domestic.graphs.graph_index import generate_garph

import matplotlib
matplotlib.use('Agg')

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

@bp.route('/graph/<graph_id>')
def get_graph(graph_id):
  graph_base64 = generate_garph(graph_id)
  if graph_base64:
    return jsonify({'graph' : graph_base64})
  else:
    return jsonify({'error' : '해당 id를 찾지 못했습니다.'}), 404