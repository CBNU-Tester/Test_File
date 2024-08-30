from django.urls import path
from .views import RecordView
from .views import SaveDBView
urlpatterns = [
    path('', RecordView.as_view(), name='record_view'),
    path('save/', SaveDBView.as_view(), name='save_db_view'),
]
