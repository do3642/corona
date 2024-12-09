# 코로나 맵 (Corona Map)

📌 **프로젝트 개요**  
COVID-19 국내 및 국외 데이터를 시각화하여 제공하는 맵 기반 웹 애플리케이션입니다.  
이 프로젝트는 Flask를 활용하여 서버를 구축하고, 데이터 시각화와 사용자 친화적인 UI를 제공합니다.

---

## 🚀 **기능 소개**
- **국내 COVID-19 데이터 시각화**  
  - 지역별 감염률, 확진자 수, 사망자 수 등을 지도와 그래프로 제공.
- **국외 COVID-19 데이터 시각화**  
  - 전 세계 국가별 COVID-19 현황 표시.
<!-- - **실시간 데이터 업데이트**  
  - 외부 API 또는 데이터베이스를 활용하여 최신 데이터를 유지. -->
- **반응형 디자인**  
  - 고려중입니다.

---

## 🛠️ **기술 스택**
- **Backend**: Flask, Python  
- **Frontend**: HTML, CSS, JavaScript  
- **Database**: MySQL  
- **환경**: Windows, Visual Studio Code  

---

## 🧑‍🤝‍🧑 **팀 구성 (4인 프로젝트)**
- **역할 분담**: (추후 작성)  
  - **데이터 수집 및 처리**  
    - 국내 및 국외 데이터 API 연동, 데이터 파싱, 저장.
  - **Backend 개발**  
    - Flask 블루프린트 설계 및 데이터 제공 API 구현.
  - **Frontend 개발**  
    - 지도 시각화 및 UI/UX 디자인 구현.
  - **프로젝트 관리**  
    - 구조 설계, 문서화, 버전 관리 (GitHub).

---

## 📜 **설치 및 실행 방법**

### 1. 프로젝트 클론
`git clone https://github.com/do3642/corona.git`
클론 후 develop 브랜치 확인

### 2. 가상환경 설정 및 활성화
가상환경 생성  
```bash
py -3.11 -m venv CoronaScope  
```

가상환경 활성화 (Windows)  
```bash
.\CoronaScope\Scripts\activate
```

### 3. 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행
```bash
flask run
```

---

## ⚙️ **환경 변수 설정 (.env)**
.env 파일은 민감한 정보를 보호하기 위해 사용됩니다. 아래는 필요한 환경 변수 목록입니다:

- **.env 파일 예시**
```python
  - FLASK_APP=apps.app.py
  - FLASK_DEBUG=True
```

⚠️ .env 파일은 .gitignore에 포함되어 있어 GitHub에 업로드되지 않습니다.

---

## 📊 **데이터 출처**
- **국내 데이터**: 질병관리청 (KCDC)  
- **국외 데이터**: World Health Organization (WHO)  

---

## 🤝 **기여 방법**
1. 이 리포지토리를 포크합니다.
2. 새로운 브랜치를 생성합니다:
   - `git branch feature/기능이름`
   - `git switch feature/기능이름`으로 작업 브랜치 전환
3. 변경 사항을 커밋합니다:
   - `git add . → git commit -m "커밋메시지"`
4. 브랜치에 푸시합니다:
   - `git push origin feature/기능이름`
5. Pull Request를 생성합니다.

---
