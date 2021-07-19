import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fbprophet.plot import add_changepoints_to_plot

df = pd.read_csv('C:/Users/SeHyun/AppData/Local/Programs/pycharm/AIAutoTrader/bitcoinprice.csv')
#df = pd.read_csv('bitcoinprice.csv') 가능
df.head()
print(df)

#df = df.reset_index() 여기선 할필요없음 엑셀에선 index가 숫자로 정상적으로 되어있음
df['Date'] = pd.to_datetime(df['Date']) #여기서 월이 문자로 표시되어있으므로 날짜형식으로 한번 바꿔줌
#df['Close'] = pd.to_numeric(df['Close']) 달러표시때문에 문자로인식하기에 작성한 코드/ 엑셀자체내에서 문자->일반으로 수정
#전체선택
# df['ds'] = df['Date']
# df['y'] = df['Ratio5n10']
# data = df[['ds','y']]
#일부선택 테스트
df['ds'] = df.loc[:1800]['Date']
df['y'] = df.loc[:1800]['Ratio5n10']
data = df[['ds','y']]

data.drop(data.index[1800:],inplace=True)
#data.drop(data.index[:60],inplace=True) #위아래 순서중요?

data=data.reset_index(drop=True)



print(data)

plt.plot(df.ds,df.y)
#plt.scatter(df.ds,df.y)
# plt.xlabel('ds') :그냥 축에 라벨 붙이는거
# plt.ylabel('y')
plt.show()



#학습
model = Prophet(changepoint_range=0.85,changepoint_prior_scale=0.2,weekly_seasonality=15) #기본 80프로에서 90프로 데이터피팅/ 유연성 0.05에서 0.5로 올림
model.fit(data)

#10일간 미래 예측
future = model.make_future_dataframe(periods=150)
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
