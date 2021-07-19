import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

#잔고조회
access = "MPkRxNHzaDjzEnnavkqRuQjxeNq0zkdYwx00wOY3"          # 본인 값으로 변경
secret = "zaY5VgKwd123fdxAtEMv57yq782UZMJpq3VfOa4s"          # 본인 값으로 변경

#상승장 타겟
def get_target_price_up(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    """# 전날과 당일 데이터 가져와서 전날의 변동성을 계산하고 오늘의 시초가( = 전날종가)와 더한 연산과정"""
    return target_price
#하락장 타겟
def get_target_price_down(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] - (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    #orderbook = pyupbit.get_orderbook("KRW-BTC") #원화시장 비트코인 호가 조회
    #bids_asks = orderbook[0]['orderbook_units']
    # json형태로 0행에 'orderbook_units'이라는 항목이있고?
    # 그안에 다시 ask_price':, 'bid_price': , 'ask_size': , 'bid_size'의 항목으로 반복된다
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]
    #[0]["ask_price"] 에서 굳이 [0]? 해야되나 싶었으나 0행에서 askprice를 찾는것이므로 이해
    #가장 최근 매도 호가 조회 = 현재가 = pyupbit.get_current_price(ticker))

"""max min 값 구하기"""
predicted_max_time = 0
predicted_min_time = 0
predicted_max_price = 0
predicted_min_price = 0
predicted_close_price = 0

def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    """ 이부분 기억 """
    global predicted_max_price
    global predicted_min_price
    global predicted_max_time
    global predicted_min_time

    df = pyupbit.get_ohlcv(ticker, interval="minute60",count=1000)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    """여기까지 러닝"""
    #아래는 자정을 기준으로 종가예측
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue

    """최대 최소 가격 구하기"""
    # 현시간 구하기
    from datetime import datetime
    now = datetime.now()
    n = now.hour
    print(n)
    """max와 min을 종가로 우선 설정"""
    """종가도 내코드에선 9시가 아니라 00시로 바꿔야할듯"""
    print("현재",pyupbit.get_current_price("KRW-BTC"),",종가",closeValue)
    maxValue = closeValue
    minValue = closeValue
    maxTime = minTime = n
    for i in range(0, 23, 1):  # n이냐 0이냐  n으로 둔다면 22시의 경우 maxt,mint가 동일하므로 거래 x 라는 장점
        nowDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=i)]
        # 현재 시간이 자정 이후
        if len(nowDf) == 0:
            nowDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=i)]  # 날짜때문에 그런듯 우리는 9시의 시간을 원하고 날짜는 00시가 돼서 바뀌므로
        """n으로 설정한다면 딱히 if가 필요없고(당일), 0으로 설정한다면 그다음날로 넘어갈수있으므로 필요하다"""
        nowValue = nowDf['yhat'].values[0]
        if maxValue < nowValue:
            maxValue = nowValue
            maxTime = i
            print(maxValue, i)
            print()

        if minValue > nowValue:
            minValue = nowValue
            minTime = i
            print(minValue, i)
    print("최종 :", maxTime, maxValue, minTime, minValue)
    predicted_max_price = maxValue
    predicted_min_price = minValue
    predicted_max_Time = maxTime
    predicted_min_Time = minTime

predict_price("KRW-BTC") #코드 실행시킬때 예측 아래코드로 한시간마다 예측 반복
#schedule.every().hour.do(lambda: predict_price("KRW-BTC")) #한시간마다 예측하라
schedule.every().halfday.do(lambda: predict_price("KRW-BTC")) #12시간마다 예측하라



# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending() #실행 예약된 작업을 실행한다

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            #target_price = get_target_price_up("KRW-BTC", 0.5)

            current_price = get_current_price("KRW-BTC")
            if predicted_min_Time
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)