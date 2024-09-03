from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from datetime import date
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def password_control(password, password_confirm, form):
    """Controllo della password inserita nel form"""
    if password and not password_confirm:
        form.add_error('password_confirm', "Conferma la nuova password.")
    elif password_confirm and not password:
        form.add_error('password', "Inserire la nuova password.")
    elif password != password_confirm:
        form.add_error('password_confirm', "Le password non corrispondono.")
    elif form.instance.user.check_password(password):
        form.add_error('password', "La nuova password non può essere la stessa della precedente.")

    if password:
        try:
            validate_password(password)  # Applica i validatori di password
        except ValidationError as e:
            for error in e.messages:
                form.add_error('password', error)


class StudentSignUpForm(UserCreationForm):
    """Form per la creazione di uno studente"""
    first_name = forms.CharField(label="Nome", required=True)
    last_name = forms.CharField(label="Cognome", required=True)
    birth_date = forms.DateField(label="Data di nascita", widget=forms.DateInput(attrs={'type': 'date'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'student@student.com'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'birth_date', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('email')
        if not email or email.count('@') != 1 or ' ' in email:
            self.add_error("email", "Indirizzo email non valido")
        elif User.objects.filter(email=email).exists():
            self.add_error("email", "Questo indirizzo email è già stato utilizzato")
        birth_date = self.cleaned_data.get('birth_date')
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 14:
            self.add_error("birth_date", "Devi avere almeno 14 anni")
        if age > 70:
            self.add_error("birth_date", "Età massima 70 anni")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Il nome deve avere solo la prima lettera maiuscola
        user.first_name = user.first_name.capitalize()
        # Nel cognome ogni lettera che inizia una parola deve essere maiuscola
        words = user.last_name.split()
        capitalized_words = [word.capitalize() for word in words]
        user.last_name = ' '.join(capitalized_words)
        user.is_student = True
        if commit:
            user.save()
            Student.objects.create(user=user)
        return user


class TutorSignUpForm(UserCreationForm):
    """Form per la creazione di un tutor"""
    first_name = forms.CharField(label="Nome", required=True)
    last_name = forms.CharField(label="Cognome", required=True)
    birth_date = forms.DateField(label='Data di nascita', widget=forms.DateInput(attrs={'type': 'date'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'tutor@tutor.com'}))
    profile_picture = forms.ImageField(label="Foto profilo", required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    location = forms.ModelChoiceField(label="Località*", queryset=Location.objects.all().order_by('name'), required=False)
    new_location = forms.CharField(label="Aggiungi nuova località (annulla il campo precedente)", max_length=50, required=False)
    subjects = forms.ModelMultipleChoiceField(label="Materie*", queryset=Subject.objects.all().order_by('name'), widget=forms.SelectMultiple, required=False)
    new_subjects = forms.CharField(label="Aggiungi nuove materie (separate da virgole)", widget=forms.Textarea, required=False)
    price_per_hour = forms.IntegerField(label="Prezzo orario (€)", initial=15, min_value=15, max_value=60, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'birth_date', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('email')
        if not email or email.count('@') != 1 or ' ' in email:
            self.add_error("email", "Indirizzo email non valido")
        elif User.objects.filter(email=email).exists():
            self.add_error("email", "Questo indirizzo email è già stato utilizzato")
        location = cleaned_data.get('location')
        new_location = cleaned_data.get('new_location')
        if not location and not new_location:
            self.add_error("location", "Devi selezionare una località esistente o inserirne una nuova")
        subjects = cleaned_data.get('subjects')
        new_subjects = cleaned_data.get('new_subjects')
        if not subjects and not new_subjects:
            self.add_error("subjects", "Devi selezionare almeno una materia o aggiungerne una nuova")
        birth_date = self.cleaned_data.get('birth_date')
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            self.add_error("birth_date", "Devi essere maggiorenne (almeno 18 anni)")
        if age > 70:
            self.add_error("birth_date", "Età massima 70 anni")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Il nome deve avere solo la prima lettera maiuscola
        user.first_name = user.first_name.capitalize()
        # Nel cognome ogni lettera che inizia una parola deve essere maiuscola
        words = user.last_name.split()
        capitalized_words = [word.capitalize() for word in words]
        user.last_name = ' '.join(capitalized_words)
        user.is_tutor = True
        if commit:
            user.save()
            if self.cleaned_data['new_location']:
                new_location = self.cleaned_data['new_location'].title()
                location, created = Location.objects.get_or_create(name=new_location)
            else:
                location = self.cleaned_data['location']
            tutor = Tutor.objects.create(user=user, location=location, price_per_hour=self.cleaned_data['price_per_hour'])
            subjects_list = list(self.cleaned_data['subjects'])
            if self.cleaned_data['new_subjects']:
                new_subjects = self.cleaned_data['new_subjects'].split(',')
                for subject_name in new_subjects:
                    subject_name = subject_name.strip()
                    if subject_name:
                        # Nel nome della materia ogni lettera che inizia una parola deve essere maiuscola
                        words = subject_name.split()
                        capitalized_words = [word.capitalize() if word not in ["e", "E"] else word for word in words]
                        subject_name = ' '.join(capitalized_words)
                        subject, created = Subject.objects.get_or_create(name=subject_name)
                        subjects_list.append(subject)
            tutor.subjects.set(subjects_list)
            if self.cleaned_data['profile_picture']:
                tutor.profile_picture = self.cleaned_data['profile_picture']
            else:
                tutor.profile_picture = 'default/default_user.png'
            tutor.bio = self.cleaned_data['bio']
            tutor.save()
        return user


class StudentEditForm(UserChangeForm):
    """Form per la modifica di uno studente"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Nuova password (opzionale)'}), required=False, label="Nuova Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Conferma nuova password'}), required=False, label="Conferma Nuova Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

        # Imposta il placeholder con il valore attuale
        self.fields['first_name'].widget.attrs['placeholder'] = self.instance.user.first_name
        self.fields['last_name'].widget.attrs['placeholder'] = self.instance.user.last_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        password_control(password, password_confirm, self)

        first_name = cleaned_data.get('first_name')
        if first_name.lower() == self.instance.user.first_name.lower():
            self.add_error('first_name', "Il nome è uguale a quello precedente")

        last_name = cleaned_data.get('last_name')
        if last_name.lower() == self.instance.user.last_name.lower():
            self.add_error('last_name', "Il cognome è uguale a quello precedente")

        return cleaned_data


class TutorEditForm(UserChangeForm):
    """Form per la modifica di uno tutor"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Nuova password (opzionale)'}), required=False, label="Nuova Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Conferma nuova password'}), required=False, label="Conferma Nuova Password")
    profile_picture = forms.ImageField(required=False, label="Foto Profilo", widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label="Bio")
    price_per_hour = forms.IntegerField(required=True, min_value=15, max_value=60, label="Prezzo orario")
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all().order_by('name'), required=False, widget=forms.SelectMultiple, label="Materie")
    new_subjects = forms.CharField(label="Aggiungi nuove materie (separate da virgole)", widget=forms.Textarea, required=False)
    location = forms.ModelChoiceField(queryset=Location.objects.all().order_by('name'), required=False, label="Location")
    new_location = forms.CharField(label="Aggiungi nuova località (annulla il campo precedente)", max_length=50, required=False)

    class Meta:
        model = User
        fields = ['profile_picture', 'bio', 'first_name', 'last_name', 'password', 'price_per_hour', 'subjects', 'location']

    def __init__(self, *args, **kwargs):
        super(TutorEditForm, self).__init__(*args, **kwargs)
        tutor = self.instance
        self.fields['first_name'].initial = tutor.user.first_name
        self.fields['last_name'].initial = tutor.user.last_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if not cleaned_data.get("profile_picture"):
            self.cleaned_data["profile_picture"] = "default/default_user.png"

        password_control(password, password_confirm, self)

        first_name = cleaned_data.get('first_name')
        if not first_name:
            self.add_error('first_name', "Il nome non può essere vuoto")

        last_name = cleaned_data.get('last_name')
        if not last_name:
            self.add_error('last_name', "Il cognome non può essere vuoto")

        location = cleaned_data.get('location')
        new_location = cleaned_data.get('new_location')
        if not location and not new_location:
            self.add_error("location", "Devi selezionare una località esistente o inserirne una nuova")
        subjects = cleaned_data.get('subjects')
        new_subjects = cleaned_data.get('new_subjects')
        if not subjects and not new_subjects:
            self.add_error("subjects", "Devi selezionare almeno una materia o aggiungerne una nuova")

        return cleaned_data
