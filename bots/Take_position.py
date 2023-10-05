import requests
import hashlib
import hmac
import time
import json
import decimal

class BinanceTrader:
    def __init__(self):
        self.base_url = 'https://fapi.binance.com'
        self.api_key = 'jtE4YTXyXmzrcreCaZ0qPpVi3DKL8QP5EkaPcLgONg8wXzcZzg6s7ezkjKWdvRkt'
        self.api_secret = 'X3MN50B6pavcsXBqNEpo2Bz0sFGjcPiPbm4Lxo4Shek1YTJMaXXiho6N7zRXJ9lK'
        self.recv_window = 60000  # Adjust the recvWindow value as needed

    def create_signature(self, query_string):
        hmac_obj = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256)
        return hmac_obj.hexdigest()

    def place_order(self, symbol, side, usdt_size, leverage):
        endpoint = '/fapi/v1/order'
        timestamp = int(time.time() * 1000)

        # Get current price
        price_endpoint = '/fapi/v1/ticker/price'
        price_params = {'symbol': symbol}
        price_response = requests.get(f"{self.base_url}{price_endpoint}", params=price_params)
        price_data = json.loads(price_response.text)
        price = float(price_data['price'])

        # Calculate quantity based on USDT size and price
        quantity = usdt_size / price

        # Retrieve asset precision
        precision_endpoint = '/fapi/v1/exchangeInfo'
        precision_response = requests.get(f"{self.base_url}{precision_endpoint}")
        precision_data = json.loads(precision_response.text)

        # Find the asset's precision
        asset_precision = None
        stopPrice_precision = None
        for symbol_info in precision_data['symbols']:
            if symbol_info['symbol'] == symbol:
                asset_precision = symbol_info['quantityPrecision']
                filters = symbol_info['filters']
                for f in filters:
                    if f['filterType'] == 'PRICE_FILTER':
                        stopPrice_precision = decimal.Decimal(f['tickSize']).as_tuple().exponent * -1
                        break
                break

        if asset_precision is None:
            raise ValueError(f"Precision information not found for symbol: {symbol}")
        if stopPrice_precision is None:
            raise ValueError(f"stopPrice_precision information not found for symbol: {symbol}")
        # Round the quantity to the asset's precision
        quantity = round(quantity, asset_precision)

        query_params = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': quantity,
            'timestamp': timestamp,
            'recvWindow': self.recv_window,
            'leverage': leverage
        }

        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        signature = self.create_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.post(url, headers=headers)
        trade = json.loads(response.text)
        return trade, stopPrice_precision

    def place_order_tp_sl(self, symbol, side, price, kind, position_id):
        endpoint = '/fapi/v1/order'
        timestamp = int(time.time() * 1000)

        opposite_side = 'SELL' if side == 'BUY' else 'BUY'
        position_info = self.get_position_info(symbol)

        params = {
            'symbol': symbol,
            'side': opposite_side,
            'type': kind,
            'stopPrice': price,
            'timestamp': timestamp,
            'timeInForce': 'GTE_GTC',
            'closePosition': True,
            'positionSide': position_info['positionSide'], # this might be remooved but not sure
            'workingType': 'MARK_PRICE',
            'recvWindow': self.recv_window
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = self.create_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.post(url, headers=headers)
        data = json.loads(response.text)

        if 'code' in data and data['code'] != 200:
            raise ValueError(f"Failed to place {kind} order for symbol {symbol}: {data}")

        return data

    def get_position_info(self, symbol, position_id=None, type_=None):
        endpoint = '/fapi/v2/positionRisk'
        timestamp = int(time.time() * 1000)
        query_params = {
            'symbol': symbol,
            'timestamp': timestamp,
            'recvWindow': self.recv_window
        }

        if position_id is not None:
            query_params['orderId'] = position_id
        if type_ is not None:
            query_params['type'] = type_

        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        signature = self.create_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)

        print("Raw Response:", response.text)  # Print the raw response to investigate further

        for position in data:
            if position['symbol'] == symbol:
                return position

        raise ValueError(f"Position information not found for symbol: {symbol}")

    def set_leverage(self, symbol, leverage):
        endpoint = '/fapi/v1/leverage'
        timestamp = int(time.time() * 1000)
        params = {
            'symbol': symbol,
            'leverage': leverage,
            'timestamp': timestamp,
            'recvWindow': self.recv_window
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = self.create_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.post(url, headers=headers)
        result = json.loads(response.text)
        return result

    def get_closed_positions(self, symbol):
        endpoint = '/fapi/v2/positionRisk'
        timestamp = int(time.time() * 1000)
        query_params = {
            'symbol': symbol,
            'timestamp': timestamp,
            'recvWindow': self.recv_window
        }

        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        signature = self.create_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.get(url, headers=headers)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            # Error decoding JSON, return empty list
            print(f"Error decoding JSON response for symbol {symbol}")
            return []

        print("Raw Response:", response.text)  # Print the raw response to investigate further

        closed_positions = []
        for position in data:
            if position['symbol'] == symbol and float(position['positionAmt']) == 0:
                closed_positions.append(position)

        return closed_positions

    def get_open_positions(self, symbol):
        endpoint = '/fapi/v2/positionRisk'
        timestamp = int(time.time() * 1000)
        query_params = {
            'symbol': symbol,
            'timestamp': timestamp,
            'recvWindow': self.recv_window
        }

        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        signature = self.create_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)

        print("Raw Response:", response.text)  # Print the raw response to investigate further

        open_positions = []
        for position in data:
            if position['symbol'] == symbol and float(position['positionAmt']) != 0:
                open_positions.append(position)

        return open_positions

    def get_ticker_price(self, symbol):
        endpoint = '/fapi/v1/ticker/price'
        params = {'symbol': symbol}
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params)
        data = json.loads(response.text)
        print(data)
        return float(data['price'])