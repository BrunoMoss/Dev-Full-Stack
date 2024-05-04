import requests
import pandas as pd
import json
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
from datetime import datetime, timedelta
from arch import arch_model
from scipy import stats

KEY = "PKL37T6EHPI3IWBKW9S5"
SECRET = "Y0fw0tsCgFwJl6eIdb4rE3Lj1hh0eFxj47D9cS78"

# API do site ALPACA para coletar os ativos que possuem dados de mercado
# disponibilizados pela API
def getAssets():
    """
    Retorna os ativos listados na API da corretorna ALPACA.

    :return: DataFrame com os ativos listados na API da corretora ALPACA.
    """   
    url = "https://paper-api.alpaca.markets/v2/assets?attributes="

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": KEY,
        "APCA-API-SECRET-KEY": SECRET
    }

    response = requests.get(url, headers=headers)

    df = pd.DataFrame(response.json())
  
    return df

# Função para coletar os ativos mais negociados.
# Acessa a api do site https://etfdb.com
def getmosttradables(n:int,page:int)->pd.DataFrame:
    """
    Coleta os ativos do tipo ETF mais negociados.

    :param int n: Número de ativos que serão retornados.
    :param int page: página da consulta que será retornada.
    :return: DataFrame com os preços de fechamento diários dos ativos consultados.
    """   
    url = "https://etfdb.com/api/screener/"

    payload = json.dumps({
    "sort_by": "average_volume",
    "sort_direction": "desc",
    "page": page,
    "per_page":n,
    "only": [
        "meta",
        "data"
    ]
    })
    headers = {
    'Accept': 'application/json',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://etfdb.com',
    'Referer': 'https://etfdb.com/screener/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = [{'symbol':c['symbol']['text'],'name':c['name']['text'],'average_volume':c['average_volume']} for c in response.json()['data']]

    df = pd.DataFrame(data)

    return df

# API so site ALPACA para coletar preços dos ativos
def getETFData(symbol_list:str,start_date:str,end_date:str)-> pd.DataFrame:
    """
    Coleta o preço de fechamento de uma lista de ativos entre a data inicial e final.

    :param int n: Número de ativos que serão retornados.
    :param datetime start_date: data inicial.
    :param datetime end_date: data final.
    :return: DataFrame com os preços de fechamento diários dos ativos consultados.
    """   

    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol_list}&timeframe=1Day&start={start_date}&end={end_date}&limit=1000&adjustment=all&feed=sip&sort=asc"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": KEY,
        "APCA-API-SECRET-KEY": SECRET
    }

    response = requests.get(url, headers=headers)
    df = pd.DataFrame()
    for symbol in symbol_list.split(','):
        if symbol in response.json()['bars']:
            df = pd.concat([df,
                            pd.DataFrame([o['c'] for o in response.json()['bars'][symbol]],columns=[symbol],
                                        index=[o['t'] for o in response.json()['bars'][symbol]])],axis=1)
    return df

def getAssetsByTradedVolumn(n:int=50):
    
    # Lista de ativos mais negociados.
    df_most_tradables = getmosttradables(500,1)

    # Lista de ativos com dados de mercado na corretora ALPACA.
    df_assets = getAssets()

    df_asset_top = df_assets.merge(df_most_tradables,how='inner', on ='symbol')

    df_asset_top['average_volume'] = [float(str(i).replace(",", "")) for i in df_asset_top['average_volume'] ]

    # Retornam os ativos mais negociados e que tenham cotação na API de dados da ALPACA
    df_asset_top.sort_values(by='average_volume',ascending=False,inplace=True)

    etf_list = df_asset_top['symbol'].unique()[0:n]

    return etf_list

def getAssetsInfo(n:int=10)-> pd.DataFrame:
    """
    Coleta os n ativos mais negociados.
   :param int n: Número de ativos que serão retornados.
   :return: DataFrame com os os ativos coletados.
   """
    if n > 500:
        raise Exception("Índice máximo da busca = 500.")

    # Lista de ativos mais negociados.
    df_most_tradables = getmosttradables(n,1)

    # Lista de ativos com dados de mercado na corretora ALPACA.
    df_assets = getAssets()

    df_assets.drop_duplicates(subset=['symbol'],inplace=True)

    df_asset_top = df_assets.merge(df_most_tradables,how='inner', on ='symbol')

    df_asset_top['average_volume'] = [float(str(i).replace(",", "")) for i in df_asset_top['average_volume'] ]

    # Retornam os ativos mais negociados e que tenham cotação na API de dados da ALPACA
    df_asset_top.sort_values(by='average_volume',ascending=False,inplace=True)

    df_asset_selected = df_asset_top[['symbol','average_volume','name_x']]

    return df_asset_selected

def getPrices(etf_list)-> pd.DataFrame:
    """
    Coleta  o preço e uma série de métricas de uma lista de ativos.
   :param etf_list: lista de ativos para coleta de preço.
   :return: DataFrame com os preços diários dos ativos consultados.
   """

    etf_list_splited = [','.join(etf_list[i:i+3]) for i in range(0, len(etf_list), 3)]

    end_date = datetime.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=365)

    prices= pd.DataFrame()

    for l in etf_list_splited:
        prices = pd.concat([prices,getETFData(l,start_date.strftime('%Y-%m-%d'),end_date.strftime('%Y-%m-%d'))],axis=1)

    prices.bfill(inplace=True)

    original_columns = list(prices.columns)

    sma3 = prices.rolling(3).mean()
    
    sma5 = prices.rolling(5).mean()
   
    ema3 = prices.ewm(span=3, adjust=False).mean()
    
    ema5 = prices.ewm(span=5, adjust=False).mean()

    prices = prices.join(sma3, rsuffix='_sma3')
    prices = prices.join(sma5, rsuffix='_sma5')
    prices = prices.join(ema3, rsuffix='_ema3')
    prices = prices.join(ema5, rsuffix='_ema5')

    prices.dropna(inplace=True)

    return prices,original_columns

