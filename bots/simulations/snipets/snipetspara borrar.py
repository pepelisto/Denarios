from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F
from django.db.models.functions import Extract

# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

# Assuming you have imported the model Closed_position_sim
# Closed_position_sim.objects.all().delete()
Closed_position_sim.objects.filter(simulation=446000339).delete()
