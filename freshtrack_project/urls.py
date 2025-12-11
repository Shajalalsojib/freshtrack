from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('freshtrack_project.freshtrack_app.urls')),
]
