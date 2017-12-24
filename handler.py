import json
import os
import logging
import requests
import boto3
from cc_privateAPI import Coincheck

CC_ACCESS_KEY = os.environ['CC_ACCESS_KEY']
CC_SECRET_KEY = os.environ['CC_SECRET_KEY']

logger = logging.getLogger()

def loktarogar(event, context):
    coincheck = Coincheck(CC_ACCESS_KEY, CC_SECRET_KEY)

    try:
        balance = get_balance(coincheck)
    except Exception as e:
        logger.error(e)
        return 'get_balance error!'

    try:
        ticker = get_ticker()
    except Exception as e:
        logger.error(e)
        return 'get_ticker error!'

    try:
        last_trade = get_last_trade()
    except Exception as e:
        logger.error(e)
        return 'get_last_trade error!'

    return last_trade

def get_balance(coincheck):
    path_balance = '/api/accounts/balance'
    result = coincheck.get(path_balance)
    return result

def get_ticker():
    path_ticker = 'https://coincheck.com/api/ticker'
    result = requests.get(path_ticker).json()
    return result

def get_last_trade():
    last_trade_table = boto3.resource('dynamodb').Table('last_trade')
    return last_trade_table.get_item(Key={'market_id': 'coincheck'})['Item']
