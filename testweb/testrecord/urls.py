from django.urls import path
from .views import save_record
urlpatterns = [
    path('save/', save_record, name='save_db'),
]
