from django.urls import path
from .views import RecordView
from .views import save_record
urlpatterns = [
    path('', RecordView.as_view(), name='record_view'),
    path('save/', save_record, name='save_db'),
]
