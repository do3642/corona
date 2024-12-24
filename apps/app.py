from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from apps.crw import views as crw_views

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)

  # MySQL 연결
  app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:1234@localhost:3306/coronamap',
    # 변경사항 감지 비활성화
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=True
  )

  # Flask와 SQLAlchemy를 연결
  db.init_app(app)
  Migrate(app, db)
  
  # crw Blueprint 등록
  from apps.crw import views as crw_views
  app.register_blueprint(crw_views.crw_bp, url_prefix='/crw')

  from apps.worldwide import views as worldwide_views
  from apps.domestic import views as domestic_views
  from apps.domestic import data as domestic_data

  app.register_blueprint(worldwide_views.worldwide_bp, url_prefix='/worldwide')
  app.register_blueprint(domestic_views.bp, url_prefix='/domestic')
  app.register_blueprint(domestic_data.bp, url_prefix='/api/graph')
  
  return app
