from django.urls import path
from .views import BaseView, ProcessView,RecordView
urlpatterns = [
    path('test/', BaseView.as_view(), name='test_view'),
    path('process/', ProcessView.as_view(), name='process_view'),
    path('',RecordView.as_view(), name='record_view')
]
