from flask import Blueprint, render_template, request, jsonify
from apps.crw.search_google import search_google
from apps.crw.search_naver import search_naver

crw_bp = Blueprint(
    'crw',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 메인 페이지 (국가 리스트)
@crw_bp.route('/')
def index():
    countries = ["South Korea", "United States", "Japan", "France", "Germany"]
    return render_template('index.html', countries=countries)


@crw_bp.route('/select-date')
def select_date():
    country = request.args.get('country')
    return jsonify({
    'status': 'success',
    'selected_country': country
    })


# 뉴스 크롤링 라우트
@crw_bp.route('/crawl', methods=['GET'])
def crawl_data():
    # 클라이언트에서 국가 이름 받기
    country = request.args.get('country')

    if not country:
        return jsonify({
            "status": "error",
            "message": "Country parameter is missing."
        }), 400

    try:
        # 검색 쿼리 생성
        search_query = f"{country} 코로나 뉴스"

        # 네이버 또는 구글로 크롤링
        # if country.lower() in ["south korea", "korea", "대한민국"]:
        #     news = search_naver(search_query)
        # else:
        #     news = search_google(search_query)

        news = search_naver(search_query)

        # 크롤링 결과 확인
        if not news:
            return jsonify({
                "status": "error",
                "message": "No news data found."
            }), 404

        # 성공적으로 데이터 반환
        return jsonify({
            "status": "success",
            "result": news
        }), 200

    except Exception as e:
        print(f"Error during crawl: {e}")  # 디버깅 로그
        return jsonify({
            "status": "error",
            "message": "An error occurred while crawling.",
            "details": str(e)
        }), 500

# 뉴스 상세 페이지 라우트
@crw_bp.route('/news-detail', methods=['GET'])
def news_detail():
    url = request.args.get('url')
    return render_template('news_detail.html', url=url)