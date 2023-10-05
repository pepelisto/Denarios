from django.contrib import admin
from django.urls import include, path
from django.conf.urls import include


urlpatterns = [
    path('', include('app.urls', namespace='app')),
    path('admin/', admin.site.urls),
]
