from django import forms
from django.core.exceptions import ValidationError
from .models import Availability


class AvailabilityForm(forms.ModelForm):
    """Form per la gestione della disponibilità"""
    class Meta:
        model = Availability
        fields = ['day', 'start', 'end']
        labels = {
            'day': 'Giorno',
            'start': 'Ora di Inizio',
            'end': 'Ora di Fine',
        }
        widgets = {
            'day': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'format': '%Y-%m-%d'}),
            'start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'format': '%H:%M'}),
            'end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'format': '%H:%M'})
        }

    def __init__(self, *args, **kwargs):
        self.tutor = kwargs.pop('tutor', None)
        super().__init__(*args, **kwargs)
        if self.initial.get('start'):
            self.initial['start'] = self.initial['start'].strftime('%H:%M')
        if self.initial.get('end'):
            self.initial['end'] = self.initial['end'].strftime('%H:%M')
        if self.initial.get('day'):
            self.initial['day'] = self.initial['day'].strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        tutor = self.tutor or self.instance.tutor

        if day and start and end:
            # Controlla se c'è una sovrapposizione di disponibilità
            if Availability.objects.filter(tutor=tutor, day=day).exclude(pk=self.instance.pk).filter(
                    start__lt=end,
                    end__gt=start
            ).exists():
                raise ValidationError("La disponibilità si sovrappone con un'altra disponibilità esistente.")

        return cleaned_data
