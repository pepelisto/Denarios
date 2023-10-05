from django.contrib import admin
from .models import *

admin.site.register(Symbol)
admin.site.register(Oportunities)
admin.site.register(Open_position)
admin.site.register(Closed_position)
# admin.site.register(Oportunities_sim)
# admin.site.register(Open_position_sim)
# admin.site.register(Closed_position_sim)
admin.site.register(Optimum_parameter)
admin.site.register(Simulations)

