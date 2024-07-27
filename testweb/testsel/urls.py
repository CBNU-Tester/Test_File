from django.urls import path
from .views import (
    BaseView, ProcessView, ProcessListView, RecordView,
    TestScheduleCreateView, TestScheduleListView, TestScheduleDetailView, TestResultListView
)

urlpatterns = [
    path('', RecordView.as_view(), name='record_view'),
    path('test/', BaseView.as_view(), name='test_view'),
    path('process/', ProcessView.as_view(), name='process_view'),
    path('processList/', ProcessListView.as_view(), name='process_list_view'),
    path('schedule/new/', TestScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/', TestScheduleListView.as_view(), name='schedule_list'),
    path('schedule/<int:pk>/', TestScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedule/<int:schedule_id>/results/', TestResultListView.as_view(), name='result_list'),
]
