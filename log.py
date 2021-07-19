import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv('C:/Users/SeHyun/AppData/Local/Programs/pycharm/AIAutoTrader/bitcoinprice.csv')
#df = pd.read_csv('bitcoinprice.csv') 가능
df.head()
print(df)

#df = df.reset_index() 여기선 할필요없음 엑셀에선 index가 숫자로 정상적으로 되어있음
df['Date'] = pd.to_datetime(df['Date']) #여기서 월이 문자로 표시되어있으므로 날짜형식으로 한번 바꿔줌

##전체선택*
df['ds'] = df['Date']
df['y'] = df['Log']
data = df[['ds','y']]
 #data = data.rename(columns={'Date':'ds,'Close':'y'}) 뭐이렇게 열의 리네이밍 가능

##최신값 날리기 위에 주석필요*; 일부선택코드(대과거데이터로 과거값 테스트)  :아래처럼 진행할경우 ds,y열을 추가로 만드는데 100번째 줄부터 데이터값이 들어가기때문에 0~99까지 값이 존재x문제발생, 즉 지워야한ㄷ
# df['ds'] = df.loc[60:]['Date']
# df['y'] = df.loc[60:]['Log']
# data = df[['ds','y']]
# data.drop(data.index[:60],inplace=True) #0~100까지 날림/ inplace로 바로 적용
# data=data.reset_index(drop=True) #인덱싱 0부터 다시 정렬 /drop=true안하면 인덱싱중복/ data= data.으로 적용

##60~600 데이터로 결과값 내기*
# df['ds'] = df.loc[60:300]['Date']
# df['y'] = df.loc[60:300]['Close']
# data = df[['ds','y']]
# data.drop(data.index[300:],inplace=True) #0~100까지 날림/ inplace로 바로 적용
# data.drop(data.index[:60],inplace=True) #0~100까지 날림/ inplace로 바로 적용
# data=data.reset_index(drop=True) #인덱싱 0부터 다시 정렬 /drop=true안하면 인덱싱중복/ data= data.으로 적용


  # 실패: data.drop(data.index[:100])
print(data)

#일반 행렬의 그래프 시행착오1
#data.plot(x='ds',y='y') 이런형식은 코랩에서만 가능한듯
#시행착오2
# plt.plot(data)
# plt.show()
#그래프 그리기 성공 https://meaownworld.tistory.com/50
plt.plot(df.ds,df.y)
plt.show()
# plt.xlabel('ds') :그냥 축에 라벨 붙이는거
# plt.ylabel('y')


#학습
model = Prophet()
model.fit(data)

#10일간 미래 예측
future = model.make_future_dataframe(periods=200)
forecast = model.predict(future)
forecast.head()
forecast.tail()#?

#prophet 그래프 시행착오
#fig1 = model.plot(forecast)
#그래프 그리기 https://dining-developer.tistory.com/25
model.plot(forecast)
plt.show() #??