from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Tc(models.Model):
    tc_num = models.AutoField(db_column='TC_Num', primary_key=True)  # Field name made lowercase.
    tc_pid = models.ForeignKey('TcList', on_delete=models.CASCADE, db_column='TC_PID', blank=True, null=True)  # 부모가 삭제되면 자식도 삭제됨
    tc_type = models.CharField(db_column='TC_Type', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tc_url = models.CharField(db_column='TC_Url', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tc_target = models.CharField(db_column='TC_Target', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tc_input = models.TextField(db_column='TC_Input', blank=True, null=True)  # Field name made lowercase.
    tc_result = models.TextField(db_column='TC_Result', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tc'


class TcList(models.Model):
    tc_pid = models.AutoField(db_column='TC_PID', primary_key=True)  # Field name made lowercase.
    tc_uid = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='TC_UID', blank=True, null=True)  # Field name made lowercase.
    tc_name = models.CharField(db_column='TC_Name', max_length=255)  # Field name made lowercase.
    tc_describe = models.TextField(db_column='TC_Describe', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tc_list'


class Ts(models.Model):
    ts_num = models.AutoField(db_column='TS_Num', primary_key=True)  # Field name made lowercase.
    tc_pid = models.ForeignKey(TcList, models.DO_NOTHING, db_column='TC_PID', blank=True, null=True)  # Field name made lowercase.
    tc_uid = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='TC_UID', blank=True, null=True)  # Field name made lowercase.
    ts_start = models.DateTimeField(db_column='TS_Start', blank=True, null=True)  # Field name made lowercase.
    ts_end = models.DateTimeField(db_column='TS_End', blank=True, null=True)  # Field name made lowercase.
    ts_iter = models.CharField(db_column='TS_Iter', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ts_day = models.CharField(db_column='TS_Day', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ts'