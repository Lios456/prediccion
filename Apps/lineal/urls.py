from django.urls import path
from . import views
urlpatterns = [
    path('prediccion/', views.predecir_humedad)
]
