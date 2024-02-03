from django.db import models


class TestSave(models.Model):
    test_save_pk = models.AutoField(db_column='Test_Save_PK', primary_key=True)  # Field name made lowercase.
    test_name = models.CharField(db_column='Test_Name', max_length=45, blank=True, null=True)  # Field name made lowercase.
    test_num = models.IntegerField(db_column='Test_Num', blank=True, null=True)  # Field name made lowercase.
    test_uid = models.CharField(db_column='Test_UID', max_length=45, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    target = models.CharField(max_length=255, blank=True, null=True)
    input = models.CharField(max_length=255, blank=True, null=True)
    result = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test_save'