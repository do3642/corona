import os
import pandas as pd
from apps.worldwide.models import WorldLatLong
from apps.app import db

def insert_data_to_db_Lat_Long():
    # CSV 파일 경로
    csv_path = os.path.join(os.getcwd(), 'apps/worldwide/static/data/WHO-COVID-19-lat-long.csv')

    # CSV 파일 읽기
    data = pd.read_csv(csv_path)

    # NaN 값 처리: NaN 값이 있으면 0으로 대체
    data['Lat'] = data['Lat'].fillna(0)
    data['Long'] = data['Long'].fillna(0)

    # 데이터베이스에 데이터를 하나씩 추가 또는 업데이트
    try:
        for _, row in data.iterrows():
            # 해당 country_code가 이미 존재하는지 확인
            existing_entry = WorldLatLong.query.filter_by(country_code=row['Country_code']).first()
            
            if existing_entry:
                # 이미 존재하면 업데이트
                existing_entry.country = row['Country']
                existing_entry.country_lat = row['Lat']
                existing_entry.country_long = row['Long']
            else:
                # 존재하지 않으면 새로 추가
                new_entry = WorldLatLong(
                    country_code=row['Country_code'],
                    country=row['Country'],
                    country_lat=row['Lat'],
                    country_long=row['Long']
                )
                db.session.add(new_entry)

        # 변경 사항을 커밋하여 데이터베이스에 저장
        db.session.commit()
        print("데이터가 성공적으로 데이터베이스에 저장되었습니다!")

    except Exception as e:
        # 예외가 발생하면 롤백
        db.session.rollback()
        print(f"데이터 저장 중 오류 발생: {e}")
