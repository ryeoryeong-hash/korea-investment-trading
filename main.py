import requests
import json
import yaml
import time
import csv
import os
from datetime import datetime


with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)


class AutoTradingSystem:
    def __init__(self, config):
        self.config = config
        self.url = "https://openapivts.koreainvestment.com:29443"
        self.token = self._get_access_token()

    def _get_access_token(self):
        body = {"grant_type": "client_credentials", "appkey": self.config['APP_KEY'],
                "appsecret": self.config['APP_SECRET']}
        res = requests.post(f"{self.url}/oauth2/tokenP", data=json.dumps(body))
        return res.json()['access_token']

    def get_current_price(self, symbol):
        headers = {"authorization": f"Bearer {self.token}", "appkey": self.config['APP_KEY'],
                   "appsecret": self.config['APP_SECRET'], "tr_id": "FHKST01010100"}
        params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": symbol}
        res = requests.get(f"{self.url}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers,
                           params=params)
        return int(res.json()['output']['stck_prpr'])

    def log_trade(self, symbol, price):

        with open('trade_log.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, "BUY", price])


if __name__ == "__main__":
    bot = AutoTradingSystem(config)
    print("=== 자동매매 시스템 시작 ===")

    is_bought = False

    while True:
        try:
            price = bot.get_current_price(config['SYMBOL'])

        
            if price <= 360000 and not is_bought:
                print(f"[매수]  현재가: {price}")
                bot.log_trade(config['SYMBOL'], price)
                is_bought = True
                print(">>> [알림] trade_log.csv에 기록되었습니다.")

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 현재가: {price}원")
            time.sleep(5)

        except Exception as e:
            print(f"시스템 오류 발생: {e}")
            time.sleep(5)