from django.urls import path
from .views import *
urlpatterns = [
    path("",index,name="index"),
    path("informe_diplomas/",index,name='informe_diplomas'),
    
]
