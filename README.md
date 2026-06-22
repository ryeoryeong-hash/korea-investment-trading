# korea-investment-trading

## KIS API 기반 자동 매매 시스템

이 프로젝트는 한투 OpenAPI를 활용한 실시간 주식 자동 매매 시스템입니다. 실시간 시세를 모니터링하고 설정된 조건에 따라 매수 로직을 수행하며, 거래 기록을 CSV 파일로 저장합니다.

### 주요 코드 구성

```python
import requests  # HTTP 통신을 위한 라이브러리 호출
import json      # JSON 데이터 처리를 위한 라이브러리 호출
import yaml      # 설정 파일(yaml) 읽기를 위한 라이브러리 호출
import time      # 대기 시간(sleep) 조절을 위한 라이브러리 호출
import csv       # CSV 파일 기록을 위한 라이브러리 호출
import os        # 운영체제 관련 기능을 위한 라이브러리 호출
from datetime import datetime  # 현재 시간 기록을 위한 모듈 호출

# 설정 파일(config.yaml)을 읽기 모드로 열어 로드함
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)  # 로드된 설정을 파이썬 딕셔너리 형태로 저장

# 자동매매 기능을 수행할 클래스 정의
class AutoTradingSystem:
    def __init__(self, config):  # 클래스 초기화 함수
        self.config = config     # 설정값을 클래스 변수로 저장
        self.url = "[https://openapivts.koreainvestment.com:29443](https://openapivts.koreainvestment.com:29443)"  # 한투 모의투자 URL 지정
        self.token = self._get_access_token()  # 클래스 생성 시 토큰을 자동 발급받음

    def _get_access_token(self):  # API 인증용 액세스 토큰 발급 함수
        body = {"grant_type": "client_credentials", "appkey": self.config['APP_KEY'],
                "appsecret": self.config['APP_SECRET']}  # API 인증 본문 데이터 구성
        res = requests.post(f"{self.url}/oauth2/tokenP", data=json.dumps(body))  # 토큰 발급 서버에 요청
        return res.json()['access_token']  # 발급받은 토큰만 추출하여 반환

    def get_current_price(self, symbol):  # 특정 종목의 현재가를 조회하는 함수
        headers = {"authorization": f"Bearer {self.token}", "appkey": self.config['APP_KEY'],
                   "appsecret": self.config['APP_SECRET'], "tr_id": "FHKST01010100"}  # API 인증 헤더 구성
        params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": symbol}  # 주식 조회 파라미터 구성
        res = requests.get(f"{self.url}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers,
                           params=params)  # 실시간 시세 API 요청
        return int(res.json()['output']['stck_prpr'])  # 응답값 중 현재가만 정수형으로 반환

    def log_trade(self, symbol, price):  # 매매 내역을 CSV 파일로 저장하는 함수
        # trade_log.csv 파일을 'a'(이어쓰기) 모드로 오픈
        with open('trade_log.csv', 'a', newline='') as f:
            writer = csv.writer(f)  # CSV 파일 쓰기 객체 생성
            # 시간, 종목명, 매매유형, 가격을 한 줄로 기록
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, "BUY", price])

# 메인 실행부
if __name__ == "__main__":
    bot = AutoTradingSystem(config)  # 클래스 인스턴스 생성
    print("=== 자동매매 시스템 시작 ===")  # 시스템 시작 문구 출력

    is_bought = False  # 중복 매수 방지를 위한 상태 플래그 초기화

    while True:  # 5초 간격으로 반복하는 무한 루프
        try:
            price = bot.get_current_price(config['SYMBOL'])  # 현재가 실시간 조회

            # 현재가가 36만원 이하이고 아직 매수하지 않았다면
            if price <= 360000 and not is_bought:
                print(f"[매수]  현재가: {price}")  # 매수 시도 출력
                bot.log_trade(config['SYMBOL'], price)  # CSV에 거래 내역 기록
                is_bought = True  # 매수 상태를 True로 변경하여 추가 매수 방지
                print(">>> [알림] trade_log.csv에 기록되었습니다.")  # 기록 완료 알림

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 현재가: {price}원")  # 현재가 출력
            time.sleep(5)  # 5초 대기

        except Exception as e:  # 오류 발생 시 예외 처리
            print(f"시스템 오류 발생: {e}")  # 오류 내용 출력
            time.sleep(5)  # 오류 발생 시에도 5초 대기 후 루프 재진행
