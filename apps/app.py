from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)

 # mysql 연결
  app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:1234@localhost:3306/coronaMap',
    # 변경사항 감지 막음
    SQLALCHEMY_TRACK_MODIFICATIONS = False,

    SQLALCHEMY_EHCO=True
  )

  # 플라스크와 sql알케미를 연결시켜주는 코드
  db.init_app(app)
  Migrate(app, db)
  

  from apps.worldwide import views as worldwide_views
  from apps.domestic import views as domestic_views

  app.register_blueprint(worldwide_views.worldwide_bp, url_prefix='/worldwide')
  app.register_blueprint(domestic_views.bp, url_prefix='/domestic')
  
  return app