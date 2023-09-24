from django.urls import path
from .views import create_robot, send_xlsx_file

urlpatterns = [
    path('', create_robot, name='create_robot'),
    path('download/', send_xlsx_file, name='send_xlsx_file')
]
