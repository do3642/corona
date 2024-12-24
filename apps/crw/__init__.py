from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # MySQL 설정
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:1234@localhost:3306/coronamap',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True
    )

    # DB 초기화 및 마이그레이션
    db.init_app(app)
    Migrate(app, db)

    # Blueprint 등록
    from apps.crw import crw_bp
    from apps.worldwide import worldwide_bp

    app.register_blueprint(crw_bp)           # /crw 경로로 등록
    app.register_blueprint(worldwide_bp)     # /worldwide 경로로 등록

    return app