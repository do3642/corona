from datetime import timedelta
import datetime
from apps.worldwide.models import WhoData, CountryTranslation
from apps.app import db
import folium

def get_covid_data_for_date(date_type):
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 - 180)
    
    today = two_years_ago
    if date_type == "yesterday":
        date = today - timedelta(days=1)
    elif date_type == "tomorrow":
        date = today + timedelta(days=1)
    else:  # "today"
        date = today

    covid_data_today = db.session.query(
        db.func.sum(WhoData.new_cases).label('total_new_cases_today'),
        db.func.sum(WhoData.new_deaths).label('total_new_deaths_today')
    ).filter(WhoData.date_reported == date).first()

    yesterday = date - timedelta(days=1)
    covid_data_yesterday = db.session.query(
        db.func.sum(WhoData.new_cases).label('total_new_cases_yesterday'),
        db.func.sum(WhoData.new_deaths).label('total_new_deaths_yesterday')
    ).filter(WhoData.date_reported == yesterday).first()

    if not covid_data_today:
        return {"error": "No data found for the selected date."}, 404

    total_new_cases_today = covid_data_today.total_new_cases_today or 0
    total_new_deaths_today = covid_data_today.total_new_deaths_today or 0
    total_new_cases_yesterday = covid_data_yesterday.total_new_cases_yesterday or 0
    total_new_deaths_yesterday = covid_data_yesterday.total_new_deaths_yesterday or 0

    new_cases_change = total_new_cases_today - total_new_cases_yesterday
    new_deaths_change = total_new_deaths_today - total_new_deaths_yesterday

    total_cases = db.session.query(
        db.func.sum(WhoData.cumulative_cases).label('total_cumulative_cases')
    ).filter(WhoData.date_reported == date).scalar()

    total_deaths = db.session.query(
        db.func.sum(WhoData.cumulative_deaths).label('total_cumulative_deaths')
    ).filter(WhoData.date_reported == date).scalar()

    total_recovered = 0

    return {
        "new_cases": total_new_cases_today,
        "new_cases_change": new_cases_change,
        "new_deaths": total_new_deaths_today,
        "new_deaths_change": new_deaths_change,
        "total_cases": total_cases,
        "total_cases_change": total_new_cases_today,
        "total_recovered": total_recovered,
        "total_recovered_change": 0,
        "total_deaths": total_deaths,
        "total_deaths_change": total_new_deaths_today
    }

def get_covid_map_and_data():
    current_date = datetime.datetime.now().date()
    two_years_ago = current_date - datetime.timedelta(days=365 * 2 - 180)

    records = db.session.query(WhoData, CountryTranslation).filter(
        WhoData.date_reported == two_years_ago,
        WhoData.country_code == CountryTranslation.country_code
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

    start_coords = [20, 0]
    world_map = folium.Map(location=start_coords, zoom_start=2)
    folium.Marker([37.5665, 126.9780], popup='Seoul, South Korea').add_to(world_map)
    folium.Marker([40.7128, -74.0060], popup='New York, USA').add_to(world_map)
    folium.Marker([48.8566, 2.3522], popup='Paris, France').add_to(world_map)

    map_html = world_map._repr_html_()

    return records, country_percentages, map_html
