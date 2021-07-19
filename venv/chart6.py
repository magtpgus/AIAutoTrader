import pyupbit
from fbprophet import Prophet
import cv #이미지 파일 다루기
import matplotlib.pyplot as plt

#BTC 최근 3년간의 데이터 불러옴
df = pyupbit.get_ohlcv("KRW-BTC", interval="minute60",count=1100)
print(df)

#ds와 y로 정리 ,prophet특징
df = df.reset_index() #왜냐하면 업비트에서 가져온 데이터는 index가 날짜로 되어있음 따라서 0,1,2,3..으로 인덱싱 
df['ds'] = df['index']
df['y'] = df['close']
data = df[['ds','y']]

#대과거로 과거 테스트할땐 위에 주석
# df['ds'] = df.loc[:1000]['index'] #이숫자는 1100을 기준으로 -n : n시간전의 데이터로 테스트하겠다
# df['y'] = df.loc[:1000]['close']
# data = df[['ds','y']]
# data.drop(data.index[1000:],inplace=True) #0~100까지 날림/ inplace로 바로 적용
# data=data.reset_index(drop=True) #인덱싱 0부터 다시 정렬 /drop=true안하면 인덱싱중복/ data= data.으로 적용

print(data)

plt.plot(df.ds,df.y)
plt.show()

#학습
model = Prophet(daily_seasonality=15)
model.fit(data)

#24시간 미래 예측
future = model.make_future_dataframe(periods=150, freq='H')
forecast = model.predict(future)
forecast.head()
#그래프1 오답
 # fig1 = model.plot(forecast,uncertainty=True)
 # forecast.head()
#그래프 정답
model.plot(forecast)
plt.show() #??

model.plot_components(forecast)
plt.show()