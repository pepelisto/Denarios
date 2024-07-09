import django
from django.conf import settings
from Denarios.settings import DATABASES, INSTALLED_APPS


django.setup()
from app.models import *


op = Optimum_parameter.objects.all()
for o in op:
    print(o)
    # o.delete()

