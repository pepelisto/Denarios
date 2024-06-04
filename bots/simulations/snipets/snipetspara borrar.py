from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F
from django.db.models.functions import Extract

# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

# Assuming you have imported the model Closed_position_sim
# # Closed_position_sim.objects.all().delete()
Closed_position_sim.objects.exclude(simulation=450000000).delete()

# symbols = Closed_position_sim.objects.values('symbol__symbol').filter(simulation=446560339).values_list('symbol__symbol', flat=True).distinct()
# print(symbols)
# sy_false = Symbol.objects.exclude(symbol__in=symbols)
# for s in sy_false:
#     s.find_in_api = False
#     s.save()