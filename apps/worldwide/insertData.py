import os
import pandas as pd
from apps.worldwide.models import WhoData
from apps.app import db

def insert_data_to_db():
    # CSV 파일 경로
    csv_path = os.path.join(os.getcwd(), 'apps/worldwide/static/data/WHO-COVID-19-global-daily-data.csv')

    # CSV 파일 읽기
    data = pd.read_csv(csv_path)

    # 데이터 확인 (Optional)
    print(f"총 {len(data)}개의 데이터가 로드되었습니다.")

    # 데이터베이스에 추가할 객체 리스트
    bulk_data = []
    for _, row in data.iterrows():
        # 각 필드에 대한 예외 처리 -> 숫자는 비어있거나 nan이면 0으로, 문자는 비어있거나 nan이면 Unknown으로
        new_cases = int(row['New_cases']) if not pd.isna(row['New_cases']) else 0
        cumulative_cases = int(row['Cumulative_cases']) if not pd.isna(row['Cumulative_cases']) else 0
        new_deaths = int(row['New_deaths']) if not pd.isna(row['New_deaths']) else 0
        cumulative_deaths = int(row['Cumulative_deaths']) if not pd.isna(row['Cumulative_deaths']) else 0
        
        country_code = row['Country_code'] if not pd.isna(row['Country_code']) else 'Unknown'
        country = row['Country'] if not pd.isna(row['Country']) else 'Unknown'
        who_region = row['WHO_region'] if not pd.isna(row['WHO_region']) else 'Unknown'

        # 중복된 데이터가 있는지 확인 (기존 데이터가 존재하면 업데이트, 없으면 새로 추가)
        existing_record = WhoData.query.filter_by(
            date_reported=row['Date_reported'],
            country_code=country_code
        ).first()

        if existing_record:
            # 데이터를 업데이트
            existing_record.new_cases = new_cases
            existing_record.cumulative_cases = cumulative_cases
            existing_record.new_deaths = new_deaths
            existing_record.cumulative_deaths = cumulative_deaths
        else:
            # 새로 데이터를 삽입
            bulk_data.append(
                WhoData(
                    date_reported=row['Date_reported'],
                    country_code=country_code,
                    country=country,
                    who_region=who_region,
                    new_cases=new_cases,
                    cumulative_cases=cumulative_cases,
                    new_deaths=new_deaths,
                    cumulative_deaths=cumulative_deaths
                )
            )

    # 데이터가 많아서 끊어서 등록
    try:
        BATCH_SIZE = 10000
        for i in range(0, len(bulk_data), BATCH_SIZE):
            db.session.bulk_save_objects(bulk_data[i:i+BATCH_SIZE])
            db.session.commit()
        print("데이터가 성공적으로 데이터베이스에 저장되었습니다!")
    except Exception as e:
        db.session.rollback()
        print(f"데이터 저장 중 오류 발생: {e}")
