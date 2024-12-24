import numpy as np
import pandas as pd
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import os
from keras.callbacks import EarlyStopping
import joblib  # joblib를 사용하여 스케일러 저장 및 로드

# 데이터 로딩 및 전처리
csv_file = "WHO-COVID-19-global-daily-data.csv"
df = pd.read_csv(csv_file)
df.fillna(0, inplace=True)

# 'Date_reported'를 datetime 형식으로 변환
df['Date_reported'] = pd.to_datetime(df['Date_reported'])

# 날짜별로 그룹화하여 각 컬럼의 합 계산
daily_summary = df.groupby('Date_reported')[
    ['New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths', 'New_Recoveries', 'Cumulative_Recoveries']
].sum().reset_index()

# 날짜를 숫자 형태로 변환
daily_summary['Date_int'] = (daily_summary['Date_reported'] - daily_summary['Date_reported'].min()).dt.days

# 입력 데이터와 출력 데이터 구성
features = ['New_cases', 'New_deaths', 'New_Recoveries', 'Cumulative_cases', 'Cumulative_deaths', 'Cumulative_Recoveries']
daily_summary[features] = daily_summary[features].shift(1).fillna(0)  # 전날 데이터로 설정
X = daily_summary[['Date_int'] + features]  # 날짜와 전날 데이터 포함
y = daily_summary[features]  # 현재 날짜의 데이터가 레이블

# 데이터 정규화
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y)

# 모델 파일 경로 설정
model_path = "covid_prediction_model.h5"
scaler_X_path = "scaler_X.pkl"  # X 스케일러 파일 경로
scaler_y_path = "scaler_y.pkl"  # y 스케일러 파일 경로

# 모델 생성 또는 불러오기
if not os.path.exists(model_path):
    # 모델 정의
    model = Sequential([
        Dense(512, activation='relu', input_shape=(X_scaled.shape[1],)),
        Dropout(0.3),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(6, activation='linear')  # 출력층에서 'linear' 활성화 함수 사용
    ])
    
    # 모델 컴파일
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    # EarlyStopping 설정
    early_stopping = EarlyStopping(monitor='loss', patience=15, restore_best_weights=True)
    
    # 모델 학습
    model.fit(X_scaled, y_scaled, epochs=200, batch_size=32, verbose=1, callbacks=[early_stopping])
    
    # 모델 저장
    model.save(model_path)
    print(f"모델이 {model_path}에 저장되었습니다.")
    
    # 스케일러 저장
    joblib.dump(scaler_X, scaler_X_path)
    joblib.dump(scaler_y, scaler_y_path)
    print(f"스케일러가 {scaler_X_path}와 {scaler_y_path}에 저장되었습니다.")
else:
    # 기존 모델 불러오기
    model = load_model(model_path)
    print(f"{model_path}에서 모델을 불러왔습니다.")
    
    # 저장된 스케일러 불러오기
    scaler_X = joblib.load(scaler_X_path)
    scaler_y = joblib.load(scaler_y_path)
    print(f"스케일러가 {scaler_X_path}와 {scaler_y_path}에서 불러와졌습니다.")

# 특정 날짜 예측
def predict_covid(date_str):
    # 예측 날짜 처리
    date_to_predict = pd.to_datetime(date_str)
    print(f"예측 날짜: {date_to_predict}")
    date_int = (date_to_predict - daily_summary['Date_reported'].min()).days
    print(f"날짜의 정수 값: {date_int}")
    
    # 예측에 사용할 입력 데이터 구성 (날짜 + 전날 데이터)
    previous_day = daily_summary[daily_summary['Date_int'] == date_int - 1][features].values
    if len(previous_day) == 0:  # 데이터가 없을 경우 기본값 사용
        previous_day = np.zeros((1, len(features)))

    print("전날 데이터:", previous_day)
    
    # 날짜를 2차원 배열로 변환
    date_array = np.array([[date_int]])  # 2차원으로 확장
    
    # 날짜와 전날 데이터를 결합
    input_data = np.hstack([date_array, previous_day])  # 차원이 일치해 결합 가능
    print("입력 데이터:", input_data)
    
    # 입력 데이터 정규화
    input_scaled = scaler_X.transform(input_data)
    print("정규화된 입력 데이터:", input_scaled)
    
    # 예측
    predicted_scaled = model.predict(input_scaled)
    predicted = scaler_y.inverse_transform(predicted_scaled)
    predicted = np.maximum(predicted, 0)
    
    # 예측 결과 출력
    print(f"날짜: {date_str}")
    print(f"예측된 새로운 확진자 수: {predicted[0][0]}")
    print(f"예측된 새로운 사망자 수: {predicted[0][1]}")
    print(f"예측된 새로운 완치자 수: {predicted[0][2]}")
    print(f"예측된 누적 확진자 수: {predicted[0][3]}")
    print(f"예측된 누적 사망자 수: {predicted[0][4]}")
    print(f"예측된 누적 완치자 수: {predicted[0][5]}")

# 사용 예시
predict_covid('2022-06-24')
