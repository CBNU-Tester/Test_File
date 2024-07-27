from django.db import models

class TestSave(models.Model):
    test_save_pk = models.AutoField(db_column='Test_Save_PK', primary_key=True)
    test_name = models.CharField(db_column='Test_Name', max_length=45, blank=True, null=True)
    test_num = models.IntegerField(db_column='Test_Num', blank=True, null=True)
    test_uid = models.CharField(db_column='Test_UID', max_length=45, blank=True, null=True)
    type = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    target = models.CharField(max_length=255, blank=True, null=True)
    input = models.CharField(max_length=255, blank=True, null=True)
    result = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test_save'

class TestSchedule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    test_cases = models.ManyToManyField(TestSave, related_name='schedules')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    repeat_interval = models.CharField(max_length=100, null=True, blank=True)  # 주기를 표현하는 필드

    def __str__(self):
        return self.name
    class Meta:
        managed = False
        db_table = 'test_schedule'

class TestResult(models.Model):
    schedule = models.ForeignKey(TestSchedule, on_delete=models.CASCADE, related_name='results')
    test_case = models.ForeignKey(TestSave, on_delete=models.CASCADE)
    result = models.TextField()
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_case.test_name} - {self.result}"

    class Meta:
        managed = False
        db_table = 'test_result'