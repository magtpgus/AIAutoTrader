import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

# 잔고조회
access = "ck7FapRGE3wM9csGvH1TfDhEvg0JxVTQDD8ObvoN"  # 본인 값으로 변경
secret = "gNDGSef3J5eQPcTpJjIGn2VE6pSo3qfcOOREaEmN"  # 본인 값으로 변경


# 상승장 타겟
def get_target_price_up(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    """# 전날과 당일 데이터 가져와서 전날의 변동성을 계산하고 오늘의 시초가( = 전날종가)와 더한 연산과정"""
    return target_price


# 하락장 타겟
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
    # orderbook = pyupbit.get_orderbook("KRW-BTC") #원화시장 비트코인 호가 조회
    # bids_asks = orderbook[0]['orderbook_units']
    # json형태로 0행에 'orderbook_units'이라는 항목이있고?
    # 그안에 다시 ask_price':, 'bid_price': , 'ask_size': , 'bid_size'의 항목으로 반복된다
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]
    # [0]["ask_price"] 에서 굳이 [0]? 해야되나 싶었으나 0행에서 askprice를 찾는것이므로 이해
    # 가장 최근 매도 호가 조회 = 현재가 = pyupbit.get_current_price(ticker))


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

    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=1000)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds', 'y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    """여기까지 러닝"""
    # 아래는 자정을 기준으로 종가예측
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
    print("현재", pyupbit.get_current_price("KRW-BTC"), ",종가", closeValue)
    maxValue = closeValue
    minValue = closeValue
    maxTime = minTime = n
    for i in range(0, 24, 1):  # n이냐 0이냐  n으로 둔다면 22시의 경우 maxt,mint가 동일하므로 거래 x 라는 장점
        nowDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=i)]
        # 현재 시간이 자정 이후
        if len(nowDf) == 0:
            nowDf = forecast[
                forecast['ds'] == data.iloc[-1]['ds'].replace(hour=i)]  # 날짜때문에 그런듯 우리는 9시의 시간을 원하고 날짜는 00시가 돼서 바뀌므로
            print("오늘", i, "가격", nowDf['yhat'].values[0])
            """n으로 설정한다면 딱히 if가 필요없고(당일), 0으로 설정한다면 그다음날로 넘어갈수있으므로 필요하다"""
        else:
            print("내일", i, "가격", nowDf['yhat'].values[0])
            i = i + 30  # 내일인 경우 i에 30시간을 더해줌으로써 maxtime> mintime (즉 자정이 지난케이스 포함)에서만 매매하게끔 하기위함
        print("i값", i)

        nowValue = nowDf['yhat'].values[0]

        if maxValue < nowValue:
            maxValue = nowValue
            # if(maxTime>nowTime)
            maxTime = i
            print("최대", maxValue, i)
            print()

        if minValue > nowValue:
            minValue = nowValue
            minTime = i
            print("최소", minValue, i)
    print("최종 :", maxTime, maxValue, minTime, minValue, "시간", get_start_time("KRW-BTC"), ",", datetime.now())
    predicted_max_price = maxValue
    predicted_min_price = minValue
    predicted_max_Time = maxTime
    predicted_min_Time = minTime


predict_price("KRW-BTC")  # 코드 실행시킬때 예측 아래코드로 한시간마다 예측 반복
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))  # 한시간마다 예측하라
# schedule.every().halfday.do(lambda: predict_price("KRW-BTC"))  # 12시간마다 예측하라

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
uuid ='x'
"""여기서 함정이 매수해서 uuid를 가지고 있어도 코드를 만약 다시 재 실행한다면 초기화됨"""
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()
        #global uuid    -while 이나 if에서는 global 할수없다
        current_price = get_current_price("KRW-BTC")

        """테스트""" #테스트 on / off , 그때 그때 시간에 맞춰서
        # predicted_max_time = 50
        # predicted_min_time = 46
        # predicted_max_price = 50000000

        """고점시간이 저점시간보다 늦은경우에만 거래"""
        if (predicted_max_time > predicted_min_time):  # min타임은 24를 넘지않고 max타임은 항상 30넘는다
            # if(predicted_min_time- datetime.timedelta(seconds=50)< now< predicted_min_time+ datetime.timedelta(seconds=50)
            #         and current_price < predicted_max_price):
            if (predicted_min_time >= 30):
                    predicted_min_time = predicted_min_time - 30
            if (predicted_min_time == now.hour and current_price < predicted_max_price):
                """여기는 성립이 안되는게 예상타임이랑 델타50초랑 호환이 안됨!!!"""
                """현재시간이 새벽 두시라면 min_t는 다음날 새벽 두시(32시)가 될수없음 즉 30을 빼도 하루차이 나서 성립되는 경우x"""
                """무작정 -30을 빼면 안됨"""
                krw = get_balance("KRW")
                if krw > 5000:
                     upbit.buy_market_order("KRW-BTC", krw * 0.0095)
                     btc = get_balance("BTC")
                     sell_price =int(current_price*1.02/1000)*1000
                     print("판매가격",sell_price, "현재가", current_price)
                     ret = upbit.sell_limit_order("KRW-BTC",sell_price,btc)
                     uuid= ret['uuid'] #매도취소를 위한 uuid

        """현시간이 고점거래인경우 btc를 들고있다면 팔아야겠지"""
        if(now.hour == predicted_max_time or now.hour == predicted_max_time-31): #테스트 할거면 predicted_max_time - 31에서 max시간을 현시간+31로 조정
            btc = get_balance("BTC")
            print(uuid)
            #upbit.cancel_order(uuid)#UUID가 없어도 밑에 매도 명령을 받는지 테스트/ 0.9995가뭔지 테스트
            if(len(uuid)!=1): #길이가 1이 아니면 uuid가 있는거고 매도주문이 걸려있는것
                print("매수시점에서의 매도주문이 존재하므로 취소합니다.")
                upbit.cancel_order(uuid)
                uuid='x'
            elif(len(upbit.get_order("KRW-BTC"))!=0):

                locked_trade = upbit.get_order("KRW-BTC")
                print("재시작으로 저장되지 않은 uuid가 존재합니다", locked_trade[0]['uuid'])
                upbit.cancel_order(locked_trade[0]['uuid'])

            else:
                print("미체결 주문 없음")
            upbit.sell_market_order("KRW-BTC", btc)
            """max와now가 24시간 차이날 경우에 대한 해결책을 생각해야됨"""
            """30을 빼지않고 31을 빼는 게 최선????"""
            """바닥에서 급등하는경우는 어떻게하지? : 그러면 min max가 1시간밖에 차이안난다는 얘기 =모순
             그리고 그 이후시간에서 max가 찍힐것이므로 하필 최저 반등시점에서 판매되지는 않을것
             특히 내일이라면 +30이 될텐데, 우리의 현재시간도 하루가 지난다면 now로 처리가능함: 00시 12시로 돌리기"""


        time.sleep(20)
    except Exception as e:
        print(e)
        time.sleep(20)

        """현재 스케쥴 schedule.every().day.at("10:30").do(job)] : 매일 4시 10시 16시 22시 로 돌리기?
        152번줄 아예 제거 가능?
        btc잔고가 있을때 파는조건 생성 1. 잔고가있어? 근데 맥스타임이야? 팔아
                                   2. 사자마자 맥스 가격에 매도주문
                                   3. 사자마자 1.5퍼 위에 매도주문 

        160번줄 조금이라도 크면? 혹은 2퍼 크면?
        """


        """0719 전체 코드 완성: 예측주기와 각 실행별 max min시간이 상이해지는것에 대한 에러사항 확인"""