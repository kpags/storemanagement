from django.contrib import admin
from django.urls import path, include
from django.views import debug

urlpatterns = [
    path('', debug.default_urlconf),
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/store/', include('store.urls')),
]
