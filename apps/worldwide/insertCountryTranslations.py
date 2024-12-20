from apps.worldwide.models import CountryTranslation
from apps.app import db

def insert_country_translations():
    country_data = [
        ('TH', '태국'),
        ('RW', '르완다'),
        ('TJ', '타지키스탄'),
        ('TZ', '탄자니아'),
        ('AI', '앙길라'),
        ('AZ', '아제르바이잔'),
        ('BD', '방글라데시'),
        ('BB', '바베이도스'),
        ('CK', '쿡 제도'),
        ('CA', '캐나다'),
        ('BR', '브라질'),
        ('CO', '콜롬비아'),
        ('DO', '도미니카 공화국'),
        ('CW', '퀴라소'),
        ('FK', '포클랜드 제도'),
        ('KM', '코모로'),
        ('IE', '아일랜드'),
        ('IM', '맨섬'),
        ('JO', '요르단'),
        ('LS', '레소토'),
        ('DM', '도미니카'),
        ('MW', '말라위'),
        ('QA', '카타르'),
        ('RO', '루마니아'),
        ('NR', '나우루'),
        ('GA', '가봉'),
        ('VC', '세인트빈센트 그레나딘'),
        ('SN', '세네갈'),
        ('LK', '스리랑카'),
        ('GP', '과들루프'),
        ('SY', '시리아 아랍 공화국'),
        ('IN', '인도'),
        ('AE', '아랍에미리트'),
        ('IR', '이란 이슬람 공화국'),
        ('SB', '솔로몬 제도'),
        ('VE', '베네수엘라 볼리바르 공화국'),
        ('PE', '페루'),
        ('TV', '투발루'),
        ('SC', '세이셸'),
        ('SS', '남수단'),
        ('AT', '오스트리아'),
        ('BE', '벨기에'),
        ('BM', '버뮤다'),
        ('BI', '부룬디'),
        ('KH', '캄보디아'),
        ('TD', '차드'),
        ('BF', '부르키나파소'),
        ('DK', '덴마크'),
        ('GF', '프랑스령 기아나'),
        ('GD', '그레나다'),
        ('JP', '일본'),
        ('JE', '저지, 채널 제도'),
        ('MC', '모나코'),
        ('NZ', '뉴질랜드'),
        ('RU', '러시아 연방'),
        ('KN', '세인트키츠 네비스'),
        ('NG', '나이지리아'),
        ('SX', '신트마르텐'),
        ('PG', '파푸아뉴기니'),
        ('TL', '동티모르'),
        ('US', '미국'),
        ('AL', '알바니아'),
        ('AG', '앤티가 바부다'),
        ('AW', '아루바'),
        ('BA', '보스니아 헤르체고비나'),
        ('BT', '부탄'),
        ('XG', '국제 운송 (솔로몬 제도)'),
        ('EE', '에스토니아'),
        ('EC', '에콰도르'),
        ('CM', '카메룬'),
        ('XF', '국제 운송 (아메리칸사모아)'),
        ('GQ', '적도 기니'),
        ('LY', '리비아'),
        ('MH', '마셜 제도'),
        ('MS', '몬트세랫'),
        ('EG', '이집트'),
        ('MN', '몽골'),
        ('GE', '조지아'),
        ('SH', '세인트헬레나'),
        ('BL', '생바르텔레미'),
        ('SM', '산마리노'),
        ('NO', '노르웨이'),
        ('CH', '스위스'),
        ('UG', '우간다'),
        ('WF', '왈리스 푸투나 제도'),
        ('SE', '스웨덴'),
        ('GB', '영국'),
        ('VU', '바누아투'),
        ('SK', '슬로바키아'),
        ('UZ', '우즈베키스탄'),
        ('AF', '아프가니스탄'),
        ('AD', '안도라'),
        ('AR', '아르헨티나'),
        ('BW', '보츠와나'),
        ('BJ', '베냉'),
        ('CV', '카보베르데'),
        ('CY', '키프로스'),
        ('GH', '가나'),
        ('GY', '가이아나'),
        ('HU', '헝가리'),
        ('CZ', '체코'),
        ('LI', '리히텐슈타인'),
        ('MV', '몰디브'),
        ('MM', '미얀마'),
        ('PH', '필리핀'),
        ('GM', '감비아'),
        ('MK', '북마케도니아'),
        ('LC', '세인트루시아'),
        ('GI', '지브롤터'),
        ('WS', '사모아'),
        ('SO', '소말리아'),
        ('GG', '건지, 채널 제도'),
        ('ID', '인도네시아'),
        ('TO', '통가'),
        ('IT', '이탈리아'),
        ('ZW', '짐바브웨'),
        ('MT', '몰타'),
        ('TM', '투르크메니스탄'),
        ('ST', '상투메 프린시페'),
        ('MP', '북마리아나 제도'),
        ('VN', '베트남'),
        ('BS', '바하마'),
        ('BH', '바레인'),
        ('CR', '코스타리카'),
        ('XL', '국제 상선'),
        ('HR', '크로아티아'),
        ('ET', '에티오피아'),
        ('KY', '케이맨 제도'),
        ('GL', '그린란드'),
        ('GW', '기니비사우'),
        ('HN', '온두라스'),
        ('IQ', '이라크'),
        ('KZ', '카자흐스탄'),
        ('LV', '라트비아'),
        ('LB', '레바논'),
        ('LU', '룩셈부르크'),
        ('KG', '키르기스스탄'),
        ('MZ', '모잠비크'),
        ('NL', '네덜란드'),
        ('LT', '리투아니아'),
        ('PY', '파라과이'),
        ('PN', '핏케언 제도'),
        ('PR', '푸에르토리코'),
        ('SA', '사우디아라비아'),
        ('MF', '생마르탱'),
        ('NE', '니제르'),
        ('DE', '독일'),
        ('RS', '세르비아'),
        ('MD', '몰도바'),
        ('SG', '싱가포르'),
        ('XI', '국제 운송 (키리바시)'),
        ('VI', '미국령 버진 제도'),
        ('TK', '토켈라우'),
        ('PM', '생피에르 미켈롱'),
        ('MY', '말레이시아'),
        ('NU', '니우에'),
        ('ES', '스페인'),
        ('OM', '오만'),
        ('DZ', '알제리'),
        ('AM', '아르메니아'),
        ('BQ', '보나에르, 신트 외스타티우스와 사바'),
        ('BN', '브루나이 다루살람'),
        ('BG', '불가리아'),
        ('DJ', '지부티'),
        ('CD', '콩고 민주 공화국'),
        ('FR', '프랑스'),
        ('SZ', '에스와티니'),
        ('PF', '프랑스 폴리네시아'),
        ('GU', '괌'),
        ('GR', '그리스'),
        ('IL', '이스라엘'),
        ('KW', '쿠웨이트'),
        ('KP', '조선민주주의인민공화국'),
        ('MG', '마다가스카르'),
        ('MA', '모로코'),
        ('PL', '폴란드'),
        ('MQ', '마르티니크'),
        ('FM', '미크로네시아 연방'),
        ('KR', '대한민국'),
        ('RE', '레위니옹'),
        ('PT', '포르투갈'),
        ('VG', '영국령 버진 제도'),
        ('CL', '칠레'),
        ('CU', '쿠바'),
        ('CI', '코트디부아르'),
        ('FJ', '피지'),
        ('GN', '기니'),
        ('CN', '중국'),
        ('HT', '아이티'),
        ('XK', '코소보 (유엔 안보리 결의 1244호(1999) 준수)'),
        ('LA', '라오스'),
        ('KI', '키리바시'),
        ('XH', '국제 운송 (바누아투)'),
        ('LR', '라이베리아'),
        ('XJ', '국제 운송 (다이아몬드 프린세스)'),
        ('MU', '모리셔스'),
        ('NA', '나미비아'),
        ('NP', '네팔'),
        ('NI', '니카라과'),
        ('PS', '서안지구 및 가자지구'),
        ('FO', '파로 제도'),
        ('PK', '파키스탄'),
        ('PW', '팔라우'),
        ('ZA', '남아프리카공화국'),
        ('SL', '시에라리온'),
        ('GT', '과테말라'),
        ('TG', '토고'),
        ('SI', '슬로베니아'),
        ('JM', '자메이카'),
        ('SR', '수리남'),
        ('ZM', '잠비아'),
        ('TR', '터키'),
        ('TC', '터크스 케이커스 제도'),
        ('YT', '마요트'),
        ('AS', '아메리칸사모아'),
        ('AO', '앙골라'),
        ('AU', '호주'),
        ('BY', '벨라루스'),
        ('BZ', '벨리즈'),
        ('BO', '볼리비아'),
        ('CF', '중앙아프리카공화국'),
        ('CG', '콩고'),
        ('ER', '에리트레아'),
        ('FI', '핀란드'),
        ('IS', '아이슬란드'),
        ('KE', '케냐'),
        ('MR', '모리타니아'),
        ('ML', '말리'),
        ('SV', '엘살바도르'),
        ('MX', '멕시코'),
        ('ME', '몬테네그로'),
        ('NC', '뉴칼레도니아'),
        ('PA', '파나마'),
        ('VA', '바티칸 시국'),
        ('UA', '우크라이나'),
        ('UY', '우루과이'),
        ('YE', '예멘'),
        ('TN', '튀니지'),
        ('TT', '트리니다드 토바고'),
        ('SD', '수단')
    ]

    try:
        for code, name in country_data:
            # 기존 레코드 확인
            existing_translation = CountryTranslation.query.filter_by(country_code=code).first()

            if existing_translation:
                # 이미 존재하는 경우 번역 업데이트
                existing_translation.country_korean = name
            else:
                # 존재하지 않는 경우 새로 추가
                new_translation = CountryTranslation(country_code=code, country_korean=name)
                db.session.add(new_translation)

        # 커밋
        db.session.commit()
        print("국가 번역 테이블에 데이터가 성공적으로 삽입/업데이트되었습니다!")
    except Exception as e:
        db.session.rollback()
        print(f"데이터 삽입/업데이트 중 오류 발생: {e}")
