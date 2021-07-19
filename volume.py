import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fbprophet.plot import add_changepoints_to_plot


df = pyupbit.get_ohlcv("KRW-BCH", interval="day1",count=1100)
print(df)


#전체선택
# df['ds'] = df['Date']
# df['y'] = df['Ratio5n10']
# data = df[['ds','y']]
#일부선택 테스트
df = df.reset_index()
df['ds'] = df.loc[:]['index']
df['y'] = df.loc[:]['volume']
data = df[['ds','y']]

#data.drop(data.index[950:],inplace=True)
#data.drop(data.index[:100],inplace=True) #위아래 순서중요

#data=data.reset_index(drop=True)



print(data)

plt.plot(df.ds,df.y)
#plt.scatter(df.ds,df.y)
# plt.xlabel('ds') :그냥 축에 라벨 붙이는거
# plt.ylabel('y')
plt.show()



#학습
model = Prophet(changepoint_range=0.9,changepoint_prior_scale=0.05)
model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
#기본 80프로에서 90프로 데이터피팅/ 유연성 0.05에서 0.5로 올림/주 패턴 10에서 20으로/달계절성 생성해서 추가
model.fit(data)

#10일간 미래 예측
future = model.make_future_dataframe(periods=160)
forecast = model.predict(future)
forecast.head()
forecast.tail()#?

#그래프 시행착오
#fig1 = model.plot(forecast)
#그래프 그리기 https://dining-developer.tistory.com/25
model.plot(forecast)
plt.show() #??

model.plot_components(forecast)
plt.show()

#https://hyperconnect.github.io/2020/03/09/prophet-package.html
# m = Prophet(
#     # trend
#     changepoint_prior_scale=0.3, #기본값 0.05
#     # seasonality
#     weekly_seasonality=10,
#     yearly_seasonality=20, #기본값 10
#     daily_seasonality=10
# )

fig = model.plot(forecast)
add_changepoints_to_plot(fig.gca(),model,forecast)
plt.show()
