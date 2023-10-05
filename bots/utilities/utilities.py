import requests
from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

def get_futures_trading_pairs(asset):
    url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    response = requests.get(url)
    data = response.json()

    trading_pairs = []
    for symbol in data['symbols']:
        base_asset = symbol['baseAsset']
        quote_asset = symbol['quoteAsset']
        if quote_asset == asset:
            trading_pair = f"{base_asset}{quote_asset}"
            trading_pairs.append(trading_pair)

    return trading_pairs

# -----------this creates one new symbol for each symbol found in binance api
# Usage get trading pairs
asset = 'BUSD'
usd_trading_pairs = get_futures_trading_pairs(asset)
print(len(usd_trading_pairs))
# for i in usd_trading_pairs:
#     new = Symbol(symbol=i)
#     new.save()

# -----------this creates one new oportunitie instance for each symbol
# symbols = Symbol.objects.all()
# for s in symbols:
#     new = Oportunities(symbol=s)
#     new.save()