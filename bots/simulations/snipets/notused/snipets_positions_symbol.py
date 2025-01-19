"""
 PPPP   EEEEE  PPPP   EEEEE   L      I   SSSSS  TTTTT   OOO
 P   P  E      P   P  E       L      I  S         T    O   O
 PPPP   EEEE   PPPP   EEEE    L      I   SSS      T    O   O
 P      E      P      E       L      I       S    T    O   O
 P      EEEEE  P      EEEEE   LLLLL  I  SSSSS     T     OOO
 """


# from django.conf import settings
import django
from datetime import datetime

from django.db.models.functions import Round

from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count,\
    ExpressionWrapper, F, Sum, IntegerField, FloatField, Case, When

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
# settings.configure()
# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)

django.setup()
from app.models import *

star_date = datetime(2024, 2, 15)
end_date = datetime(2024, 5, 31)

result = Closed_position_sim.objects.filter(close_date__range=(star_date, end_date),
           symbol__symbol='LINKUSDT',
           simulation=450000000,
          # sl_limit=0.1,# sl_low_limit=0.01,# ratr=0.05,# type='SELL',
           rsi_open=6,
          )

# Now the result will contain the statistics calculated for each combination
for entry in result:
    print(entry)

