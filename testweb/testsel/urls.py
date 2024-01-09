from django.urls import path
from .views import BaseView, ProcessView
urlpatterns = [
    path('test/', BaseView.as_view(), name='test_view'),
    path('process/', ProcessView.as_view(), name='process_view')
]
