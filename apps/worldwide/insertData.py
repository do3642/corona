import os
import pandas as pd
from apps.worldwide.models import WhoData
from apps.app import db

def insert_data_to_db():
    # CSV 파일 경로
    csv_path = os.path.join(os.getcwd(), 'apps/worldwide/static/data/WHO-COVID-19-global-daily-data.csv')

    # CSV 파일 읽기
    data = pd.read_csv(csv_path)
    
    # 필수 필드 값 비어 있는 행 제거
    data = data.dropna(subset=['Date_reported', 'Country_code'])
    print(f"총 {len(data)}개의 데이터가 로드되었습니다.")

    bulk_insert_data = []
    bulk_update_data = []

    # 데이터 분리 (삽입 vs 업데이트)
    existing_records = {
        (record.date_reported, record.country_code): record
        for record in WhoData.query.with_entities(WhoData.date_reported, WhoData.country_code).all()
    }

    for idx, row in data.iterrows():
        new_cases = int(row['New_cases']) if not pd.isna(row['New_cases']) else 0
        cumulative_cases = int(row['Cumulative_cases']) if not pd.isna(row['Cumulative_cases']) else 0
        new_deaths = int(row['New_deaths']) if not pd.isna(row['New_deaths']) else 0
        cumulative_deaths = int(row['Cumulative_deaths']) if not pd.isna(row['Cumulative_deaths']) else 0
        new_recoveries = int(row['New_Recoveries']) if not pd.isna(row['New_Recoveries']) else 0
        cumulative_recoveries = int(row['Cumulative_Recoveries']) if not pd.isna(row['Cumulative_Recoveries']) else 0

        country_code = row['Country_code'] if not pd.isna(row['Country_code']) else 'Unknown'
        country = row['Country'] if not pd.isna(row['Country']) else 'Unknown'
        who_region = row['WHO_region'] if not pd.isna(row['WHO_region']) else 'Unknown'

        key = (row['Date_reported'], country_code)

        if key in existing_records:
            bulk_update_data.append({
                "key": key,
                "new_cases": new_cases,
                "cumulative_cases": cumulative_cases,
                "new_deaths": new_deaths,
                "cumulative_deaths": cumulative_deaths,
                "new_recoveries": new_recoveries,
                "cumulative_recoveries": cumulative_recoveries,
            })
        else:
            bulk_insert_data.append(
                WhoData(
                    date_reported=row['Date_reported'],
                    country_code=country_code,
                    country=country,
                    who_region=who_region,
                    new_cases=new_cases,
                    cumulative_cases=cumulative_cases,
                    new_deaths=new_deaths,
                    cumulative_deaths=cumulative_deaths,
                    new_recoveries=new_recoveries,
                    cumulative_recoveries=cumulative_recoveries
                )
            )

        # 진행 상황 출력
        if (idx + 1) % 10000 == 0:
            print(f"처리 중: {idx + 1}/{len(data)}")

    # 새 데이터 삽입
    try:
        BATCH_SIZE = 5000
        for i in range(0, len(bulk_insert_data), BATCH_SIZE):
            db.session.bulk_save_objects(bulk_insert_data[i:i + BATCH_SIZE])
            db.session.commit()
            print(f"{i + BATCH_SIZE}/{len(bulk_insert_data)} 삽입 완료")
        print("새 데이터 삽입 완료!")
    except Exception as e:
        db.session.rollback()
        print(f"삽입 중 오류 발생: {e}")

    # 기존 데이터 업데이트
    try:
        for idx, record in enumerate(bulk_update_data):
            db.session.query(WhoData).filter_by(
                date_reported=record["key"][0], country_code=record["key"][1]
            ).update(
                {
                    "new_cases": record["new_cases"],
                    "cumulative_cases": record["cumulative_cases"],
                    "new_deaths": record["new_deaths"],
                    "cumulative_deaths": record["cumulative_deaths"],
                    "new_recoveries": record["new_recoveries"],
                    "cumulative_recoveries": record["cumulative_recoveries"]
                }
            )
            # 중간 진행 상황 확인
            if (idx + 1) % 10000 == 0:
                db.session.commit()
                print(f"{idx + 1}/{len(bulk_update_data)} 업데이트 완료")
        db.session.commit()
        print("기존 데이터 업데이트 완료!")
    except Exception as e:
        db.session.rollback()
        print(f"업데이트 중 오류 발생: {e}")
