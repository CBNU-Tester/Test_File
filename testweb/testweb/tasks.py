from django_q.tasks import async_task
from django.utils import timezone
from .models import TestSchedule, TestResult, TestSave

def run_test_schedule(schedule_id):
    schedule = TestSchedule.objects.get(id=schedule_id)
    for test_case in schedule.test_cases.all():
        # 실제 테스트 실행 로직 추가
        result = "성공"  # 테스트 실행 결과
        TestResult.objects.create(schedule=schedule, test_case=test_case, result=result, executed_at=timezone.now())

def schedule_test(schedule_id):
    async_task('my_app.tasks.run_test_schedule', schedule_id)
