from django import forms
from .models import TestSchedule, TestSave

class TestScheduleForm(forms.ModelForm):
    test_cases = forms.ModelMultipleChoiceField(
        queryset=TestSave.objects.all().order_by('test_num'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Test Cases"
    )
    scheduled_time = forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'type': 'datetime-local'}))
    repeat_interval = forms.CharField(max_length=100, required=False)

    class Meta:
        model = TestSchedule
        fields = ['name', 'description', 'scheduled_time', 'repeat_interval', 'test_cases']
