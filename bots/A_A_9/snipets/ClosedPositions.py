

from django.conf import settings
import django
from datetime import datetime
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When
from django.db.models import Q


django.setup()
from app.models import *

op = Closed_position.objects.filter(symbol__symbol="LINKUSDT")
profit = 0

for o in op:
    print(o)
    profit += o.profit
    # o.delete()
print(profit)

