import json
import os
import requests
import logging
from cc_privateAPI import Coincheck

CC_ACCESS_KEY = os.environ['CC_ACCESS_KEY']
CC_SECRET_KEY = os.environ['CC_SECRET_KEY']

logger = logging.getLogger()

def loktarogar(event, context):
    coincheck = Coincheck(CC_ACCESS_KEY, CC_SECRET_KEY)

    try:
        balance_json = get_balance(coincheck)
        balance_jpy = balance_json['jpy']
        balance_btc = balance_json['btc']
    except Exception as e:
        logger.error(e)
        return 'get_balance error!'

    try:
        ticker_json = get_ticker()
    except Exception as e:
        logger.error(e)
        return 'get_ticker error!'


    return ticker_json

def get_balance(coincheck):
    path_balance = '/api/accounts/balance'
    result = coincheck.get(path_balance)
    return result

def get_ticker():
    path_ticker = 'https://coincheck.com/api/ticker'
    result = requests.get(path_ticker).json()
    return result