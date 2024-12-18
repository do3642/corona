from datetime import timedelta
import datetime
from folium.plugins import MarkerCluster
from sqlalchemy import func
from keras.models import load_model
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd


from apps.worldwide.models import WhoData, CountryTranslation,WorldLatLong
from apps.app import db

# 모델 경로 및 모델 로드
model_path = os.path.join(os.path.dirname(__file__), 'models', 'covid_prediction_model.h5')
model = load_model(model_path)

# 예측 함수
def predict_covid(date_str):
    # 입력 날짜 처리
    date_to_predict = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    print('예측 날짜:', date_to_predict)
    
    # 두 년 반 전의 기준 날짜 계산
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)
    date_int = (date_to_predict - two_years_ago).days
    
    # 예측에 사용할 입력 데이터 구성 (날짜 + 전날 데이터)
    # 여기서는 예시로, 해당 날짜에 대한 데이터 및 이전 날짜에 대한 데이터를 넣는 방식으로 처리
    previous_day = get_total_data_for_date(date_to_predict - datetime.timedelta(days=1))  # 어제 데이터 호출
    today_data = get_total_data_for_date(date_to_predict)  # 오늘 데이터 호출
    
    # 이전 날짜 데이터를 2차원 배열로 변환
    previous_day_array = np.array([[
        previous_day['new_cases'], previous_day['new_deaths'], previous_day['new_recoveries'], 
        previous_day['cumulative_cases'], previous_day['cumulative_deaths'], previous_day['cumulative_recoveries']
    ]])
    
    # 오늘 날짜 데이터를 2차원 배열로 변환
    today_array = np.array([[
        today_data['new_cases'], today_data['new_deaths'], today_data['new_recoveries'],
        today_data['cumulative_cases'], today_data['cumulative_deaths'], today_data['cumulative_recoveries']
    ]])
    
    # 데이터 정규화
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    previous_day_scaled = scaler_X.fit_transform(previous_day_array)
    today_scaled = scaler_X.transform(today_array)
    
    # 예측
    predicted_yesterday = model.predict(previous_day_scaled)
    predicted_today = model.predict(today_scaled)

    # 예측 값들 간의 변화 계산
    new_cases_change = predicted_today[0] - predicted_yesterday[0]
    new_deaths_change = predicted_today[1] - predicted_yesterday[1]
    new_recoveries_change = predicted_today[2] - predicted_yesterday[2]
    total_cases_change = predicted_today[3] - predicted_yesterday[3]
    total_recoveries_change = predicted_today[4] - predicted_yesterday[4]
    total_deaths_change = predicted_today[5] - predicted_yesterday[5]

    # 결과 반환
    return {
        "new_cases": predicted_today[0],
        "new_cases_change": new_cases_change,
        "new_recoveries": predicted_today[2],
        "new_recoveries_change": new_recoveries_change,
        "new_deaths": predicted_today[1],
        "new_deaths_change": new_deaths_change,
        "total_cases": predicted_today[3],
        "total_cases_change": total_cases_change,
        "total_recoveries": predicted_today[4],
        "total_recoveries_change": total_recoveries_change,
        "total_deaths": predicted_today[5],
        "total_deaths_change": total_deaths_change
    }

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
def get_covid_data_for_date(date_type):
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)
    
    if date_type == "today":
        today = two_years_ago
    elif date_type == "yesterday":
        today = two_years_ago - timedelta(days=1)
    elif date_type == "tomorrow":
        today = two_years_ago + timedelta(days=1)
    else:
        today = two_years_ago + timedelta(days=1)  # 예측을 위한 날짜 설정
        print("예측 날짜:", today)

        # 예측 모델 호출 (오늘 예측 값 받기)
        predicted_today = predict_covid(today.strftime('%Y-%m-%d'))  # 예측된 오늘 값
        
         # 예측된 어제 날짜 (예시로 예측 모델을 통해 어제 날짜도 예측할 수 있습니다)
        predicted_yesterday = predict_covid((today - timedelta(days=1)).strftime('%Y-%m-%d'))  # 예측된 어제 값

        # 예측 값들 간의 변화 계산
        new_cases_change = predicted_today[0] - predicted_yesterday[0]
        new_deaths_change = predicted_today[1] - predicted_yesterday[1]
        new_recoveries_change = predicted_today[2] - predicted_yesterday[2]
        total_cases_change = predicted_today[3] - predicted_yesterday[3]
        total_recoveries_change = predicted_today[4] - predicted_yesterday[4]
        total_deaths_change = predicted_today[5] - predicted_yesterday[5]

        return {
            "new_cases": predicted_today[0],
            "new_cases_change": new_cases_change,
            "new_recoveries": predicted_today[2],
            "new_recoveries_change": new_recoveries_change,
            "new_deaths": predicted_today[1],
            "new_deaths_change": new_deaths_change,
            "total_cases": predicted_today[3],
            "total_cases_change": total_cases_change,
            "total_recoveries": predicted_today[4],
            "total_recoveries_change": total_recoveries_change,
            "total_deaths": predicted_today[5],
            "total_deaths_change": total_deaths_change
        }

    # 오늘과 어제의 데이터를 DB에서 조회하여 반환
    covid_data_today = get_total_data_for_date(today)
    covid_data_yesterday = get_total_data_for_date(today - timedelta(days=1))

    # 변화량 계산
    new_cases_change = covid_data_today["new_cases"] - covid_data_yesterday["new_cases"]
    new_deaths_change = covid_data_today["new_deaths"] - covid_data_yesterday["new_deaths"]
    new_recoveries_change = covid_data_today["new_recoveries"] - covid_data_yesterday["new_recoveries"]

    return {
        "new_cases": covid_data_today["new_cases"],
        "new_cases_change": new_cases_change,
        "new_recoveries": covid_data_today["new_recoveries"],
        "new_recoveries_change": new_recoveries_change,
        "new_deaths": covid_data_today["new_deaths"],
        "new_deaths_change": new_deaths_change,
        "total_cases": covid_data_today["cumulative_cases"],
        "total_cases_change": covid_data_today["new_cases"],
        "total_recoveries": covid_data_today["cumulative_recoveries"],
        "total_recoveries_change": covid_data_today["new_recoveries"],
        "total_deaths": covid_data_today["cumulative_deaths"],
        "total_deaths_change": covid_data_today["new_deaths"]
    }



def get_covid_map_and_data():
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)

    records = db.session.query(WhoData, CountryTranslation, WorldLatLong).filter(
        WhoData.date_reported == two_years_ago,
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


