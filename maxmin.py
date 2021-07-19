import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fbprophet.plot import add_changepoints_to_plot


# predicted_close_price = 0
#
# def predict_price(ticker):
#     """Prophet으로 당일 종가 가격 예측"""
#     global predicted_close_price
#     df = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=1100)
#     df = df.reset_index()
#     df['ds'] = df['index']
#     df['y'] = df['close']
#     data = df[['ds','y']]
#     model = Prophet()
#     model.fit(data)
#     future = model.make_future_dataframe(periods=24, freq='H')
#     forecast = model.predict(future)
#     closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
#     if len(closeDf) == 0:
#         closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
#     closeValue = closeDf['yhat'].values[0]
#     predicted_close_price = closeValue
#
#
# predict_price("KRW-BTC")
# schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

df = pyupbit.get_ohlcv("KRW-BTC", interval="minute60",count=1000)
df = df.reset_index()
df['ds'] = df['index']
df['y'] = df['close']
data = df[['ds','y']]
model = Prophet()
model.fit(data)
future = model.make_future_dataframe(periods=24, freq='H')
forecast = model.predict(future)
model.plot(forecast)
plt.show()

nowValue = pyupbit.get_current_price("KRW-BTC")
print(nowValue)

# #종가의 가격을 구함
#현재 시간이 자정 이전
closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
#현재 시간이 자정 이후
if len(closeDf) == 0:
  closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]#날짜때문에 그런듯 우리는 9시의 시간을 원하고 날짜는 00시가 돼서 바뀌므로
#어쨋든 당일 종가
closeValue = closeDf['yhat'].values[0]

#현시간 구하기
from datetime import datetime
now = datetime.now()
n = now.hour
print(n)
#최대 최소값 구하기
maxValue = closeValue
minValue = closeValue
maxTime = minTime = n
for i in range(0, 23, 1): #n이냐 0이냐  n으로 둔다면 22시의 경우 maxt,mint가 동일하므로 거래 x 라는 장점
    nowDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=i)]

    # print(nowValue)

    # 현재 시간이 자정 이후
    if len(nowDf) == 0:
        nowDf = forecast[
            forecast['ds'] == data.iloc[-1]['ds'].replace(hour=i)]  # 날짜때문에 그런듯 우리는 9시의 시간을 원하고 날짜는 00시가 돼서 바뀌므로

    nowValue = nowDf['yhat'].values[0]
    # closeValue = closeDf['yhat'].values[0]
    if maxValue < nowValue:
        maxValue = nowValue
        maxTime = i
        print(maxValue, i)
        print()

    if minValue > nowValue:
        minValue = nowValue
        minTime = i
        print(minValue, i)

print(maxValue, maxTime, minValue, minTime)

