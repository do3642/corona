from datetime import timedelta
import datetime
from folium.plugins import MarkerCluster
from sqlalchemy import func
from keras.models import load_model
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import joblib
from decimal import Decimal



from apps.worldwide.models import WhoData, CountryTranslation,WorldLatLong
from apps.app import db


# 모델 경로 및 모델 로드
model_path = os.path.join(os.path.dirname(__file__), 'models', 'covid_prediction_model.h5')
model = load_model(model_path)
# 저장된 스케일러 파일 경로
scaler_X_path = os.path.join(os.path.dirname(__file__), 'models', 'scaler_X.pkl')
scaler_y_path = os.path.join(os.path.dirname(__file__), 'models', 'scaler_y.pkl')

# 저장된 스케일러 불러오기
scaler_X = joblib.load(scaler_X_path)
scaler_y = joblib.load(scaler_y_path)


# 예측 함수
def predict_covid(date_str):
    try:
        # 예측 날짜 처리
        date_to_predict = pd.to_datetime(date_str)
        
        # 날짜 정수화 (훈련 데이터 기준)
        date_int = (date_to_predict - pd.to_datetime('2020-01-04')).days  # 훈련 시작 날짜 기준
        
        # 실제 데이터에서 전날 데이터 가져오기
        covid_data_yesterday = get_total_data_for_date(date_to_predict - timedelta(days=1))
        previous_day_data = np.array([
            float(covid_data_yesterday[key]) for key in ['new_cases', 'new_deaths', 'new_recoveries', 'cumulative_cases', 'cumulative_deaths', 'cumulative_recoveries']
        ]).reshape(1, -1)

        # 날짜 정보 추가
        date_array = np.array([[date_int]])  # 날짜 정보 2D 배열로
        # 입력 데이터 결합 (날짜 정보 + 전날 데이터)
        input_data = np.hstack([date_array, previous_day_data])  # 차원이 일치해 결합 가능
        # 입력 데이터 정규화
        input_scaled = scaler_X.transform(input_data)
        
        # 예측
        predicted_scaled = model.predict(input_scaled)
        predicted = scaler_y.inverse_transform(predicted_scaled)  # 원래 스케일로 복원
        predicted = np.maximum(predicted, 0)  # 음수는 0으로 처리

        # # 예측 결과 출력
        # print(f"예측 날짜: {date_str}")
        # print(f"예측된 새로운 확진자 수: {predicted[0][0]}")
        # print(f"예측된 새로운 사망자 수: {predicted[0][1]}")
        # print(f"예측된 새로운 완치자 수: {predicted[0][2]}")
        # print(f"예측된 누적 확진자 수: {predicted[0][3]}")
        # print(f"예측된 누적 사망자 수: {predicted[0][4]}")
        # print(f"예측된 누적 완치자 수: {predicted[0][5]}")

        # 예측된 값을 Decimal로 변환하여 반환
        return {key: Decimal(str(predicted[0][i])).quantize(Decimal('1.')) for i, key in enumerate(
            ['new_cases', 'new_deaths', 'new_recoveries', 'cumulative_cases', 'cumulative_recoveries', 'cumulative_deaths'])}


    except Exception as e:
        print(f"오류 발생: {e}")
        return None


def get_total_data_for_date(date):
    return {
        "new_cases": db.session.query(db.func.sum(db.func.coalesce(WhoData.new_cases, 0))).filter(WhoData.date_reported == date).scalar() or 0,
        "new_deaths": db.session.query(db.func.sum(db.func.coalesce(WhoData.new_deaths, 0))).filter(WhoData.date_reported == date).scalar() or 0,
        "new_recoveries": db.session.query(db.func.sum(db.func.coalesce(WhoData.new_recoveries, 0))).filter(WhoData.date_reported == date).scalar() or 0,
        "cumulative_cases": db.session.query(db.func.sum(WhoData.cumulative_cases)).filter(WhoData.date_reported == date).scalar() or 0,
        "cumulative_recoveries": db.session.query(db.func.sum(WhoData.cumulative_recoveries)).filter(WhoData.date_reported == date).scalar() or 0,
        "cumulative_deaths": db.session.query(db.func.sum(WhoData.cumulative_deaths)).filter(WhoData.date_reported == date).scalar() or 0
    }


# 날짜에 따른 COVID-19 데이터 반환 함수
import datetime
from datetime import timedelta

# 날짜에 따른 COVID-19 데이터 반환 함수
def get_covid_data_for_date(date_type):
    
    # 기본 날짜를 2년 6개월 전으로 세팅
    base_date = datetime.datetime.now().date() - timedelta(days=365 * 2 + 180)

    # 날짜 타입에 따른 날짜 계산
    date_mapping = {
        "today": base_date,
        "yesterday": base_date - timedelta(days=1),
        "tomorrow": base_date + timedelta(days=1),
        "prediction": base_date + timedelta(days=1),  # 예측할 날짜
    }

    # 잘못된 date_type 처리
    if date_type not in date_mapping:
        raise ValueError(f"잘못된 데이터 타입: {date_type}")

    selected_date = date_mapping[date_type]

    # 예측 데이터 처리
    if date_type == "prediction":
        return _get_predicted_data(selected_date)

    # 실제 데이터 처리
    return _get_actual_data(selected_date)

# 실제 데이터 반환 함수
def _get_actual_data(date):
    today_data = get_total_data_for_date(date)
    yesterday_data = get_total_data_for_date(date - timedelta(days=1))

    return _calculate_changes(today_data, yesterday_data)

# 예측 데이터 반환 함수
def _get_predicted_data(date):
    today_data = predict_covid(date)
    yesterday_data = get_total_data_for_date(date - timedelta(days=1))

    return _calculate_changes(today_data, yesterday_data)

# 변화량 계산 함수
def _calculate_changes(today_data, yesterday_data):
    return {
        "new_cases": today_data["new_cases"],
        "new_cases_change": today_data["new_cases"] - yesterday_data["new_cases"],
        "new_recoveries": today_data["new_recoveries"],
        "new_recoveries_change": today_data["new_recoveries"] - yesterday_data["new_recoveries"],
        "new_deaths": today_data["new_deaths"],
        "new_deaths_change": today_data["new_deaths"] - yesterday_data["new_deaths"],
        "total_cases": today_data["cumulative_cases"],
        "total_cases_change": today_data["new_cases"],
        "total_recoveries": today_data["cumulative_recoveries"],
        "total_recoveries_change": today_data["new_recoveries"],
        "total_deaths": today_data["cumulative_deaths"],
        "total_deaths_change": today_data["new_deaths"],
    }




def get_covid_map_and_data(selected_date=None):
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)
    # selected_date가 제공되었으면 해당 날짜로, 아니면 기본값 두 년 반 전 날짜 사용
    if selected_date:
       # selected_date가 문자열이라면 날짜로 변환, 이미 datetime.date 객체라면 그대로 사용
        if isinstance(selected_date, str):
            selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = two_years_ago

    records = db.session.query(WhoData, CountryTranslation, WorldLatLong).filter(
        WhoData.date_reported == selected_date,
        WhoData.country_code == CountryTranslation.country_code,
        WhoData.country_code == WorldLatLong.country_code
    ).distinct(WhoData.country).all()

    total_new_cases = sum(record[0].new_cases for record in records)

    country_percentages = []
    for record in records:
        who_data = record[0]
        country_translation = record[1]

        if total_new_cases > 0:
            percentage = (who_data.new_cases / total_new_cases) * 100
            country_percentages.append({
                'country': who_data.country,
                'country_korean': country_translation.country_korean,
                'percentage': round(percentage, 2)
            })


     # 마커 데이터 생성
    marker_data = []
    for record in records:
        lat = record[2].country_lat
        lng = record[2].country_long
        country = record[0].country
        country_korean = record[1].country_korean
        marker_data.append({
            'lat': lat,
            'lng': lng,
            'country': country,
            'country_korean' : country_korean
        })


  

    return records, country_percentages, marker_data


def get_date_range(period):
    """
    기간(period)에 따라 시작일을 계산
    :param period: 'daily', 'weekly', 'monthly'
    :return: 시작일과 종료일 (start_date, end_date)
    """
    current_date = datetime.datetime.now().date() - datetime.timedelta(days=365 * 2 + 180)
    if period == 'daily':
        return current_date, current_date
    elif period == 'weekly':
        start_date = current_date - datetime.timedelta(days=7)
        return start_date, current_date
    elif period == 'monthly':
        start_date = current_date - datetime.timedelta(days=30)
        return start_date, current_date
    else:
        raise ValueError("Invalid period specified. Use 'daily', 'weekly', or 'monthly'.")

def fetch_data_by_period(country, period):
    """
    특정 기간(period)의 데이터를 조회
    :param country: 국가 이름
    :param period: 'daily', 'weekly', 'monthly'
    :return: 해당 기간의 데이터 딕셔너리
    """
    start_date, end_date = get_date_range(period)
    
    # 기간별 데이터 조회
    query = db.session.query(
        func.sum(WhoData.new_cases).label('new_cases'),
        func.sum(WhoData.new_recoveries).label('new_recoveries'),
        func.sum(WhoData.new_deaths).label('new_deaths')
    ).filter(
        WhoData.date_reported.between(start_date, end_date),
        WhoData.country == country
    ).first()

    # 데이터가 없으면 0으로 반환
    return {
        "new_cases": query.new_cases or 0,
        "new_recoveries": query.new_recoveries or 0,
        "new_deaths": query.new_deaths or 0
    }


