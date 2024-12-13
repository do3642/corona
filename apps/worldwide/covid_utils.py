from datetime import timedelta
import datetime
import folium
from folium.plugins import MarkerCluster
import json
import os


from apps.worldwide.models import WhoData, CountryTranslation,WorldLatLong
from apps.app import db


def get_total_data_for_date(date):
    return {
        "new_cases": db.session.query(db.func.sum(db.func.coalesce(WhoData.new_cases, 0))).filter(WhoData.date_reported == date).scalar() or 0,
        "new_deaths": db.session.query(db.func.sum(db.func.coalesce(WhoData.new_deaths, 0))).filter(WhoData.date_reported == date).scalar() or 0,
        "new_recoveries": db.session.query(db.func.sum(db.func.coalesce(WhoData.new_recoveries, 0))).filter(WhoData.date_reported == date).scalar() or 0,
        "cumulative_cases": db.session.query(db.func.sum(WhoData.cumulative_cases)).filter(WhoData.date_reported == date).scalar() or 0,
        "cumulative_recoveries": db.session.query(db.func.sum(WhoData.cumulative_recoveries)).filter(WhoData.date_reported == date).scalar() or 0,
        "cumulative_deaths": db.session.query(db.func.sum(WhoData.cumulative_deaths)).filter(WhoData.date_reported == date).scalar() or 0
    }

def get_covid_data_for_date(date_type):
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 + 180)
    today = two_years_ago if date_type == "today" else (two_years_ago - timedelta(days=1) if date_type == "yesterday" else two_years_ago + timedelta(days=1))

    covid_data_today = get_total_data_for_date(today)
    covid_data_yesterday = get_total_data_for_date(today - timedelta(days=1))

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
        marker_data.append({
            'lat': lat,
            'lng': lng,
            'country': country
        })


  

    return records, country_percentages, marker_data