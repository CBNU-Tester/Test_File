from django.urls import path
from .views import RecordView, record_start, create_test_case

urlpatterns = [
    path('', RecordView.as_view(), name='record_view'),
    path('start/', record_start, name='selenium_record'),
    path('components/', create_test_case, name='testcase_create'),
]
