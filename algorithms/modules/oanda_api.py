import requests
import json
import pandas as pd
import datetime as dt

rest_url = "https://api-fxpractice.oanda.com/"
stream_url = "https://stream-fxpractice.oanda.com/"
access_token = "7504cc953a3efe6542a1b0181f7a69b0-f5e662a814de4b0d43ea9c206a8e44ce"
account_id = "101-001-17749174-001"
authorization_header = {'Authorization':f'Bearer {access_token}','Accept-Datetime-Format':'UNIX', 'Content-type':'application/json'}

def get_candlestick_data(instrument,periods,granularity):
    """Returns pandas dataframe of ohlc and volume data"""
    end_point = f"v3/instruments/{instrument}/candles?granularity={granularity}&count={periods}"
    r = requests.get(rest_url+end_point, headers=authorization_header)
    if "errorMessage" in json.loads(r.text).keys():
        print('Error retrieving data')
    else:
        dic = json.loads(r.content)
        candles = dic['candles']
        df = pd.DataFrame()
        df['Open'] = [float(candle['mid']['o']) for candle in candles]
        df['High'] = [float(candle['mid']['h']) for candle in candles]
        df['Low'] = [float(candle['mid']['l']) for candle in candles]
        df['Close'] = [float(candle['mid']['c']) for candle in candles]
        df['Volume'] = [float(candle['volume']) for candle in candles]
        df.index = [dt.datetime.fromtimestamp(float(candle['time'])) for candle in candles]
        return df

def get_balance():
    """Returns float representing available cash"""
    end_point = f"v3/accounts/{account_id}"
    r = requests.get(rest_url+end_point, headers=authorization_header)
    return float(json.loads(r.content)['account']['balance'])

def get_account():
    end_point = f"v3/accounts/{account_id}"
    r = requests.get(rest_url+end_point, headers=authorization_header)
    return json.loads(r.content)['account']

def market_order(instrument, qty, stop_loss, take_profit):
    """Sends market order, FOK: filled or killed"""
    end_point = f"v3/accounts/{account_id}/orders"
    data =  {"order": {
                "stopLossOnFill": {
                  "timeInForce": "GTC",
                  "price": str(stop_loss)
                },
                "takeProfitOnFill": {
                  "price": str(take_profit)
                },
                "units": str(qty),
                "instrument": instrument,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT"}
            }
    r = requests.post(rest_url+end_point, json=data, headers=authorization_header)
    print(r)
    dic = json.loads(r.text)
    if 'errorMessage' in dic.keys():
        print(f'Unable to complete order for | {qty} | {instrument} | stoploss:{stop_loss} | takeprofit:{take_profit}')
    else:
        print(f'Order for | {qty} | {instrument} | stoploss:{stop_loss} | takeprofit:{take_profit} | completed')
