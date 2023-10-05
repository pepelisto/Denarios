from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('analisis/', views.analisis, name='analisis'),  # No date parameters
    path('analisis/mensual/<str:year>/<str:month>/', views.analisis, name='analisis_mensual'),
    path('analisis/anual/<str:year>', views.analisis, name='analisis_anual'),
    path('analisis/<str:year>/<str:symbol>', views.analisis, name='analisis_symbol'),  # No date parameters
    path('analisis/<str:year>/<str:month>/<str:symbol>', views.analisis, name='analisis_symbol_mensual'),
    # path('analisis/<str:start_date>/<str:end_date>/', views.analisis, name='analisis_with_dates'),
    # With date parameters
]