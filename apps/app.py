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
    
    # worldwide Blueprint 등록
    from apps.worldwide import views as worldwide_views
    app.register_blueprint(worldwide_views.worldwide_bp, url_prefix='/worldwide')

    # crw Blueprint 등록
    from apps.crw import views as crw_views
    app.register_blueprint(crw_views.crw_bp, url_prefix='/crw')

    # 국가별 크롤링 API 추가
    @app.route('/crawl-news', methods=['POST'])
    def crawl_news():
        data = request.get_json()
        country = data.get("country")
        country_english = data.get("countryEnglish")

        if not country or not country_english:
            return jsonify({"error": "Invalid data"}), 400

        try:
            # 크롤링 처리 로직 호출
            from apps.crw.crawler import crawl_news_by_country
            news = crawl_news_by_country(country_english)
            return jsonify({"news": news})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app
