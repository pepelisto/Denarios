
import django
import datetime
from Denarios.settings import DATABASES, INSTALLED_APPS

django.setup()
from app.models import *

Open_position.objects.create(
    symbol_id=5,
    type="BUY",
    entry_price=152.23,
    leverage=19,
    quantity=160,
    margin=(160 / 19),
    open_date=datetime.datetime.now(),
    stoch=80,
    rsi=52,
    sl_price=150.6,
    tp_price=156.6,
    stopPrice_precision=5,
    timeframe=240,
    sl_order_id=6519819516,
    tp_order_id=6519849819,
    id_position=2265161,
    alt_TP_SL=0,
)