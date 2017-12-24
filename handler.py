import json
import os
import decimal
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
        ticker.update({'last': int(ticker['last']),
                       'bid' : int(ticker['bid']),
                       'ask' : int(ticker['ask'])})
    except Exception as e:
        logger.error(e)
        return 'get_ticker error!'

    try:
        last_trade_table = boto3.resource('dynamodb').Table('last_trade')
        last_trade = get_last_trade(last_trade_table)
    except Exception as e:
        logger.error(e)
        return 'get_last_trade error!'

    if last_trade['trade_type'] == 'ask':
        logger.info('前回取引が売りの為、買いを伺います')
        if ticker['last'] <= last_trade['rate']:
            logger.info('終値が前回のレートより低いので、レートを更新して様子見をします')
            try:
                last_trade.update({'rate': ticker['last']})
                last_trade_table.put_item(Item=last_trade)
                logger.info('レートを' + str(last_trade['rate']) + 'に更新しました')
            except Exception as e:
                logger.error(e)
                return 'bid_wait error!'
        else:
            pass
    else:
        pass

    return last_trade


def get_balance(coincheck):
    path_balance = '/api/accounts/balance'
    result = coincheck.get(path_balance)
    return result

def get_ticker():
    path_ticker = 'https://coincheck.com/api/ticker'
    result = requests.get(path_ticker).json()
    return result

def get_last_trade(last_trade_table):
    return last_trade_table.get_item(Key={'market_id': 'coincheck'})['Item']

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)