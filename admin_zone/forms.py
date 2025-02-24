# admin_zone/forms.py

from django import forms

class TimeSettingsForm(forms.Form):
    work_hours_start = forms.TimeField(
        label='Начало рабочего времени',
        widget=forms.TimeInput(attrs={'class': 'form-control'}),
    )
    work_hours_end = forms.TimeField(
        label='Конец рабочего времени',
        widget=forms.TimeInput(attrs={'class': 'form-control'}),
    )
    new_order_notify_interval = forms.IntegerField(
        label='Интервал уведомления новых заказов (в минутах)',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    repeat_order_notify_interval = forms.IntegerField(
        label='Интервал повторного уведомления (в минутах)',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    allow_non_working_hours_notifications = forms.BooleanField(
        label='Разрешить уведомления вне рабочего времени',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
