from django.conf import settings
import django
from bots.A_A_9.functions.Take_position import BinanceTrader

from Denarios.settings import DATABASES, INSTALLED_APPS
settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from app.models import *
# sy = Optimum_parameter.objects.get(symbol__symbol='BTCUSDT')
# sy.q = 120
# sy.save()

sy = Optimum_parameter.objects.all()
for s in sy:
    sy.factor_ajuste = 0.015
    sy.save()