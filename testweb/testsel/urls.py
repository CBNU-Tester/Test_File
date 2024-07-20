from django.urls import path
from .views import BaseView, ProcessView,RecordView, ProcessListView
urlpatterns = [
    path('test', BaseView.as_view(), name='test_view'),
    path('process', ProcessView.as_view(), name='process_view'),
    path('processList', ProcessListView.as_view(), name='process_list_view'),
    path('',RecordView.as_view(), name='record_view')
]
