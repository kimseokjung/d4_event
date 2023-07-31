from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

urlpatterns = [
    path("index/", views.index, name='index'),
    #     path("start_countdown/<int:event_id>/",
    #          views.start_countdown, name='start_countdown'),
    path("stop_countdown/",
         views.stop_countdown, name='stop_countdown'),
    # path("create_data/",
    #      views.create_data, name='create_data'),
]
