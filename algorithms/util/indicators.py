import numpy as np

def ADX(df,n):
    "function to calculate ADX"
    df['TR'] = ATR(df)['TR'] #the period parameter of ATR function does not matter because period does not influence TR calculation
    df['DMplus']=np.where((df['High']-df['High'].shift(1))>(df['Low'].shift(1)-df['Low']),df['High']-df['High'].shift(1),0)
    df['DMplus']=np.where(df['DMplus']<0,0,df['DMplus'])
    df['DMminus']=np.where((df['Low'].shift(1)-df['Low'])>(df['High']-df['High'].shift(1)),df['Low'].shift(1)-df['Low'],0)
    df['DMminus']=np.where(df['DMminus']<0,0,df['DMminus'])
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = df['TR'].tolist()
    DMplus = df['DMplus'].tolist()
    DMminus = df['DMminus'].tolist()
    for i in range(len(df)):
        if i < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == n:
            TRn.append(df['TR'].rolling(n).sum().tolist()[n])
            DMplusN.append(df['DMplus'].rolling(n).sum().tolist()[n])
            DMminusN.append(df['DMminus'].rolling(n).sum().tolist()[n])
        elif i > n:
            TRn.append(TRn[i-1] - (TRn[i-1]/14) + TR[i])
            DMplusN.append(DMplusN[i-1] - (DMplusN[i-1]/14) + DMplus[i])
            DMminusN.append(DMminusN[i-1] - (DMminusN[i-1]/14) + DMminus[i])
    df['TRn'] = np.array(TRn)
    df['DMplusN'] = np.array(DMplusN)
    df['DMminusN'] = np.array(DMminusN)
    df['DIplusN']=100*(df['DMplusN']/df['TRn'])
    df['DIminusN']=100*(df['DMminusN']/df['TRn'])
    df['DIdiff']=abs(df['DIplusN']-df['DIminusN'])
    df['DIsum']=df['DIplusN']+df['DIminusN']
    df['DX']=100*(df['DIdiff']/df['DIsum'])
    ADX = []
    DX = df['DX'].tolist()
    for j in range(len(df)):
        if j < 2*n-1:
            ADX.append(np.NaN)
        elif j == 2*n-1:
            ADX.append(df['DX'][j-n+1:j+1].mean())
        elif j > 2*n-1:
            ADX.append(((n-1)*ADX[j-1] + DX[j])/n)
    df['ADX']=np.array(ADX)

def ATR(df,n=14):
    "function to calculate True Range and Average True Range"
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df = df.drop(['H-L','H-PC','L-PC'],axis=1)

def BollingerBand(df,n):
    "function to calculate Bollinger Band"
    df["BB_MA"] = df['Adj Close'].rolling(n).mean()
    df["BB_up"] = df["MA"] + 2*df["MA"].rolling(n).std()
    df["BB_dn"] = df["MA"] - 2*df["MA"].rolling(n).std()
    df["BB_width"] = df["BB_up"] - df["BB_dn"]
    df.dropna(inplace=True)

def CMF(df,n=21):
    """Chaikan Money Flow"""
    df['CMF'] = ((((df['Close']-df['Low']) - (df['High'] - df['Close']))/(df['High'] - df['Low']))*df['Volume'])/df['Volume'].rolling(n).sum()

def EMA(df,n):
    df[f'EMA {n}'] = df['Close'].ewm(n,min_periods=n).mean()

def Engulfing(df):
    signals = [np.nan]
    for i in range(len(df)):
        if i > 0:
            prev_red = df['Close'][i-1] < df['Open'][i-1]
            cur_green = df['Close'][i] > df['Open'][i]
            if prev_red and cur_green:
                prev_width = abs(df['Close'][i-1]-df['Open'][i-1])
                cur_width = abs(df['Close'][i] - df['Open'][i])
                if prev_width < cur_width:
                    signals.append(100) #Bullish signal at price
                else:
                    signals.append(0) #no signal
            elif not prev_red and not cur_green:
                prev_width = abs(df['Close'][i-1]-df['Open'][i-1])
                cur_width = abs(df['Close'][i] - df['Open'][i])
                if prev_width < cur_width:
                    signals.append(-100) #Bearish signal at price
                else:
                    signals.append(0) #no signal
            else:
                signals.append(0)
    df['Engulfing'] = signals

def fractals(df):
    bear_fractals = [np.nan]*len(df)
    bull_fractals = [np.nan]*len(df)
    for i in range(2,len(df)-2):
        high = df['High'][i]
        low = df['Low'][i]

        if high > df['High'][i-1] and high > df['High'][i-2] and high > df['High'][i+1] and high > df['High'][i+2]:
            bear_fractals[i] = df['High'][i]
        if low < df['Low'][i-1] and low < df['Low'][i-2] and low < df['Low'][i+1] and low < df['Low'][i+2]:
            bull_fractals[i] = df['Low'][i]
    df['bull_fractals'] = bull_fractals
    df['bear_fractals'] = bear_fractals

def KijunSen(df,n=26):
    df['Kijun Sen'] = (df['High'].rolling(n).max() + df['High'].rolling(n).min())/2

def MA(df, n):
    df[f'MA {n}'] = df['Close'].rolling(n).mean()

def MACD(df,a=12,b=26,c=9):
    """function to calculate MACD
    typical values a = 12; b =26, c =9"""
    df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()

def OBV(df):
    """function to calculate On Balance Volume"""
    df['daily_ret'] = df['Adj Close'].pct_change()
    df['direction'] = np.where(df['daily_ret']>=0,1,-1)
    df['direction'][0] = 0
    df['vol_adj'] = df['Volume'] * df['direction']
    df['obv'] = df['vol_adj'].cumsum()

def ParabolicSAR(df):
    pass

def RSI(df,n=14):
    "function to calculate RSI"
    df['delta']=df['Close'] - df['Close'].shift(1)
    df['gain']=np.where(df['delta']>=0,df['delta'],0)
    df['loss']=np.where(df['delta']<0,abs(df['delta']),0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
            avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
    df['avg_gain']=np.array(avg_gain)
    df['avg_loss']=np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    df['RSI'] = 100 - (100/(1+df['RS']))
    df = df.drop(columns=['delta', 'gain', 'loss','avg_gain','avg_loss','RS'])

def STC(df):
    """Shaff Trend Cycle"""
    pass

def Stochastic(df, n=14, m=3):
    df['stoch'] = (df['Close'] - df['Low'].rolling(n).min())/(df['High'].rolling(14).max() - df['Low'].rolling(n).min())*100
    df['stoch_ma'] = df['stoch'].rolling(m).mean()

def SSL_Channel(df, n=14):
    up = [np.nan]*n
    dn = [np.nan]*n
    trend = None
    for i in range(n,len(df)):
        highs = [df['High'][k] for k in range(i-n, i)]
        high_avg = sum(highs)/len(highs)
        lows = [df['Low'][k] for k in range(i-n, i)]
        low_avg = sum(lows)/len(lows)

        close = df['Close'][i]
        if close > high_avg:
            up.append(high_avg)
            dn.append(low_avg)
            trend = 'up'
        elif close < low_avg:
            up.append(low_avg)
            dn.append(high_avg)
            trend = 'dn'
        else:
            if trend == 'up':
                up.append(high_avg)
                dn.append(low_avg)
            elif trend == 'dn':
                up.append(low_avg)
                dn.append(high_avg)

    df['SSL_up'] = up
    df['SSL_dn'] = dn

def SuperTrend(df,m=1,n=10):
    """function to calculate Supertrend given historical candle data
        m = multiplier
        n = n day ATR"""
    ATR(df,n=5) # Usually ATR_5 is used for the calculation
    df["B-U"]=((df['High']+df['Low'])/2) + m*df['ATR']
    df["B-L"]=((df['High']+df['Low'])/2) - m*df['ATR']
    df["temp1"] = df["B-U"]
    df["temp2"] = df["B-L"]
    df["F-U"]= np.where((df["B-U"]<df["temp1"].shift(1))|(df["Close"].shift(1)>df["temp1"].shift(1)),df["B-U"],df["temp1"].shift(1))
    df["F-L"]= np.where((df["B-L"]>df["temp2"].shift(1))|(df["Close"].shift(1)<df["temp2"].shift(1)),df["B-L"],df["temp2"].shift(1))
    df["Strend"] = np.where(df["Close"]<=df["F-U"],df["F-U"],df["F-L"])

def TDI(df, m=1.6185):
    """Traders Dynamic Index"""
    RSI(df, n=13)
    df['VB up'] = df['RSI'].rolling(34).mean() + m*df['RSI'].rolling(34).std()
    df['VB dn'] = df['RSI'].rolling(34).mean() - m*df['RSI'].rolling(34).std()
    df['RSI MA Fast'] = df['RSI'].rolling(2).mean()
    df['RSI MA Slow'] = df['RSI'].rolling(7).mean()

def WaveTrend(df, n1=10, n2=21):
    df['Avg Price'] = (df['Close']+df['High']+df['Low'])/3
    df['esa'] = df['Avg Price'].ewm(n1).mean()
    df['d'] = abs(df['Avg Price']-df['esa']).ewm(n1).mean()
    df['ci'] = (df['Avg Price']-df['esa'])/(0.015*df['d'])
    #Plot these vvvv
    df['tci'] = df['ci'].ewm(n2).mean()
    df['wt2'] = df['tci'].rolling(4).mean()

def WilliamsAlligator(df):
    """Alligator indicator"""
    pass
