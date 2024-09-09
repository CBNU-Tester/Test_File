from django.apps import AppConfig

class TestselConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testsel'

    def ready(self):
        # start_scheduler 함수를 한 번만 실행하기 위한 플래그를 확인
        from .tasks import start_scheduler
        if not hasattr(start_scheduler, "_initialized"):
            start_scheduler._initialized = True
            print("스케줄러 시작")
            start_scheduler()
