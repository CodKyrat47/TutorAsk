from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form per la gestione di una recensione"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Valutazione',
            'comment': 'Commento'
        }
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),  # La valutazione va da 1 a 5
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
