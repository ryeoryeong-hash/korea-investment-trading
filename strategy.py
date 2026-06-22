class TradingStrategy:
    def __init__(self, target_price):
        """
        target_price: 매수를 결정할 기준 가격
        """
        self.target_price = target_price

    def decide(self, current_price):
        """
        현재가를 입력받아 'BUY' 혹은 'HOLD'를 결정합니다.
        """
        # 현재가가 목표 가격보다 낮거나 같으면 매수 결정
        if current_price <= self.target_price:
            return "BUY"
        else:
            return "HOLD"