

from django.conf import settings
import django
from datetime import datetime
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When
from django.db.models import Q
#
# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

op = Oportunities.objects.values_list('symbol__symbol', flat=True)
# par = Optimum_parameter.objects.exclude(symbol__symbol__in=op).delete()
print(op)


# op.delete()


# print(Symbol.objects.all())