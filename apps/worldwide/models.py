from apps.app import db

class WhoData(db.Model):
    __tablename__ = 'who_data'  # 테이블 이름 정의

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 기본 키
    date_reported = db.Column(db.Date,index=True, nullable=False)  # 보고 날짜
    country_code = db.Column(db.String(10), index=True, nullable=True)  # 국가 코드 (ISO 3자리)
    country = db.Column(db.String(255), nullable=False)  # 국가명
    who_region = db.Column(db.String(50), nullable=True)  # WHO 지역

    new_cases = db.Column(db.Integer, nullable=True)  # 신규 확진자 수
    cumulative_cases = db.Column(db.Integer, nullable=True)  # 누적 확진자 수
    
    new_recoveries = db.Column(db.Integer, nullable=True)  # 신규 완치자 수
    cumulative_recoveries = db.Column(db.Integer, nullable=True)  # 누적 완치자 수

    new_deaths = db.Column(db.Integer, nullable=True)  # 신규 사망자 수
    cumulative_deaths = db.Column(db.Integer, nullable=True)  # 누적 사망자 수



class CountryTranslation(db.Model):
    __tablename__ = 'country_translation'

    country_code = db.Column(db.String(10), primary_key=True)  # 국가 코드 (ISO 3자리)
    country_korean = db.Column(db.String(255), nullable=False)  # 한글 국가명


class WorldLatLong(db.Model):
    __tablename__ = 'world_lat_long'

    country_code = db.Column(db.String(10), primary_key=True)  # 국가 코드 (ISO 3자리)
    country = db.Column(db.String(255), nullable=False)  # 국가명
    country_lat = db.Column(db.Float, nullable=False)  # 위도
    country_long = db.Column(db.Float, nullable=False)  # 경도