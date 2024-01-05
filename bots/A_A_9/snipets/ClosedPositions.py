

from django.conf import settings
import django
from datetime import datetime
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When
from django.db.models import Q


django.setup()
from app.models import *

op = Closed_position.objects.filter()

for o in op:
    print(o)
    # o.delete()


