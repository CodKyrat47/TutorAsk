from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from .forms import *
from django.contrib.auth.views import LoginView, LogoutView
from lessons.models import *
from reviews.models import *
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
import threading
from django.utils.html import strip_tags
from django.db.models import Q
from django.contrib import messages


def send_welcome_mail(form):
    """Invia una mail di benvenuto al nuovo utente"""
    def send_mail_task(subj, normal, source, recipient, html):
        try:
            send_mail(subj, normal, source, recipient, html_message=html)
        except Exception as e:
            print(f"Errore durante l'invio dell'email: {e}")

    subject = 'Benvenuto su TutorAsk'
    html_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px; background-color: #f9f9f9;">
                <h3>Benvenuto su TutorAsk!</h3>
                <p>Siamo lieti che tu ti sia registrato su TutorAsk.</p>
                <p>Da oggi puoi iniziare a esplorare tutte le funzionalità della nostra piattaforma.</p>
                <p>Cordiali saluti,<br><strong>Il team di TutorAsk</strong></p>
                <hr style="border: none; border-top: 1px solid #e0e0e0;">
                <p style="font-size: 12px; color: #777;">Questa è una email automatica, per favore non rispondere.</p>
            </div>
        </body>
        </html>
        '''
    message = strip_tags(html_message)
    email_from = 'noreply.tutorask2024@gmail.com'
    recipient_list = [form.cleaned_data.get('email')]
    thread = threading.Thread(target=send_mail_task, args=(subject, message, email_from, recipient_list, html_message))
    thread.start()


def send_profile_changes(user):
    """Invia una mail di avviso per la modifica del profilo"""
    def send_mail_task(subj, normal, source, recipient, html):
        try:
            send_mail(subj, normal, source, recipient, html_message=html)
        except Exception as e:
            print(f"Errore durante l'invio dell'email: {e}")

    subject = 'Modifica credenziali'
    html_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px; background-color: #f9f9f9;">
                <h3>Salve {user.get_full_name()},</h3>
                <p>Le confermiamo che le sue credenziali sono state modificate con successo.</p>
                <p>Cordiali saluti,<br><strong>Il team di TutorAsk</strong></p>
                <hr style="border: none; border-top: 1px solid #e0e0e0;">
                <p style="font-size: 12px; color: #777;">Questa è una email automatica, per favore non rispondere.</p>
            </div>
        </body>
        </html>
        '''
    message = strip_tags(html_message)
    email_from = 'noreply.tutorask2024@gmail.com'
    recipient_list = [user.email]
    thread = threading.Thread(target=send_mail_task, args=(subject, message, email_from, recipient_list, html_message))
    thread.start()


def send_profile_elimination(user):
    """Invia una mail per confermare l'eliminazione del profilo"""
    def send_mail_task(subj, normal, source, recipient, html):
        try:
            send_mail(subj, normal, source, recipient, html_message=html)
        except Exception as e:
            print(f"Errore durante l'invio dell'email: {e}")

    subject = 'Eliminazione profilo'
    html_message = f'''
       <html>
       <body style="font-family: Arial, sans-serif; line-height: 1.6;">
           <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px; background-color: #f9f9f9;">
               <h3>Gentile {user.get_full_name()},</h3>
               <p>Ci dispiace che tu voglia lasciarci.</p>
               <p>Se lo vorrai, potrai sempre ritornare. Ti aspettiamo!</p>
               <p>Cordiali saluti,<br><strong>Il team di TutorAsk</strong></p>
               <hr style="border: none; border-top: 1px solid #e0e0e0;">
               <p style="font-size: 12px; color: #777;">Questa è una email automatica, per favore non rispondere.</p>
           </div>
       </body>
       </html>
       '''
    message = strip_tags(html_message)
    email_from = 'noreply.tutorask2024@gmail.com'
    recipient_list = [user.email]
    thread = threading.Thread(target=send_mail_task, args=(subject, message, email_from, recipient_list, html_message))
    thread.start()


def user_signup(request):
    """View per la scelta del tipo di utente da creare"""
    return render(request, template_name="users/registration/user_signup.html")


class StudentSignUpView(CreateView):
    """View per la creazione di uno studente"""
    form_class = StudentSignUpForm
    template_name = 'users/registration/student_signup.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account creato con successo!')
        send_welcome_mail(form)
        return response


class TutorSignUpView(CreateView):
    """View per la creazione di un tutor"""
    form_class = TutorSignUpForm
    template_name = 'users/registration/tutor_signup.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account creato con successo!')
        send_welcome_mail(form)
        return response


class CustomLoginView(LoginView):
    """View per il login di un utente"""
    template_name = 'users/registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        next_url = self.request.POST.get('next')

        if next_url:
            return redirect(next_url)
        if self.request.user.is_superuser:
            return redirect('home')
        elif self.request.user.is_student:
            return redirect('users:student_profile')
        elif self.request.user.is_tutor:
            return redirect('users:tutor_profile_detail')
        return response


class CustomLogoutView(LogoutView):
    """View per il logout di un utente"""
    template_name = 'users/registration/logged_out.html'


class StudentProfileView(UpdateView):
    """View per la modifica del profilo di uno studente e per la gestione lezioni"""
    model = Student
    form_class = StudentEditForm
    template_name = 'users/student_profile.html'
    success_url = reverse_lazy('users:student_profile')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_student:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user.student

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reputation_score'] = self.get_object().reputation_score
        now = datetime.now()

        # Recupera le lezioni passate e future di uno studente
        context['past_bookings'] = Booking.objects.filter(
            Q(booked_for__day__lt=now.date()) |
            Q(booked_for__day=now.date(), booked_for__start__lt=now.time())
        ).filter(student=self.get_object()).order_by('-booked_for__day', '-booked_for__start', '-booked_for__end')

        context['upcoming_bookings'] = Booking.objects.filter(
            Q(booked_for__day__gt=now.date()) |
            Q(booked_for__day=now.date(), booked_for__start__gte=now.time())
        ).filter(student=self.get_object()).order_by('booked_for__day', 'booked_for__start', 'booked_for__end')

        return context

    def form_valid(self, form):
        student = form.save(commit=False)

        password = form.cleaned_data.get('password')
        if password:
            student.user.set_password(password)
            update_session_auth_hash(self.request, student.user)  # Mantiene l'utente loggato dopo aver cambiato la password

        first_name = form.cleaned_data.get('first_name')
        if first_name:
            student.user.first_name = first_name.capitalize()

        last_name = form.cleaned_data.get('last_name')
        if last_name:
            words = last_name.split()
            capitalized_words = [word.capitalize() for word in words]
            student.user.last_name = ' '.join(capitalized_words)

        if password or first_name or last_name:
            student.user.save()
            messages.success(self.request, 'Account aggiornato con successo!')
            send_profile_changes(student.user)
        return super().form_valid(form)


def delete_profile_confirm(request):
    """View per la conferma dell'eliminazione di un profilo"""
    if not request.user.is_authenticated or request.user.is_superuser:
        error_message = "Non hai i permessi per accedere a questa pagina."
        return render(request, 'not_authenticated.html', {'message': error_message})
    if request.method == 'POST':
        user = request.user
        if user.is_student:
            # Recupera i tutor che hanno ricevuto una recensione dallo studente
            reviews = Review.objects.filter(student__user=user)
            tutors = set(reviews.values_list('tutor', flat=True))
            # Recupera gli studenti che hanno ricevuto un voto sulle proprie recensioni dallo studente
            reviews = ReviewVote.objects.filter(student__user=user).values_list('review', flat=True)
            students = set(Student.objects.filter(student_reviews__in=reviews))
            send_profile_elimination(user)
            user.delete()
            for tutor_pk in tutors:
                tutor = Tutor.objects.get(pk=tutor_pk)
                # Aggiorna il rating del tutor
                tutor.update_average_rating()
            for student_pk in students:
                student = Student.objects.get(pk=student_pk)
                # Aggiorna la reputazione dello studente
                student.update_reputation()
        elif user.is_tutor:
            # Recupera gli studenti che hanno lasciato una recensione al tutor
            reviews = Review.objects.filter(tutor__user=user)
            students = set(Student.objects.filter(student_reviews__in=reviews))
            send_profile_elimination(user)
            user.delete()
            for student_pk in students:
                student = Student.objects.get(pk=student_pk)
                # Aggiorna la reputazione dello studente
                student.update_reputation()
        messages.success(request, 'Account eliminato con successo!')
        return redirect('users:login')
    return render(request, 'users/delete_profile_confirm.html')


class TutorProfileDetailView(DetailView):
    """View per visualizzare il profilo del tutor"""
    model = Tutor
    template_name = 'users/tutor_profile_detail.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_tutor:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        return Tutor.objects.get(user=self.request.user)


class TutorProfileUpdateView(UpdateView):
    """View per la modifica dei dati di un tutor"""
    model = User
    form_class = TutorEditForm
    template_name = 'users/user_profile_form.html'
    success_url = reverse_lazy('users:tutor_profile_detail')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_tutor:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        return Tutor.objects.get(user=self.request.user)

    def form_valid(self, form):
        tutor = self.get_object()

        password = form.cleaned_data.get('password')
        if password:
            tutor.user.set_password(password)
            update_session_auth_hash(self.request, tutor.user)  # Mantiene l'utente loggato

        # Le prime lettere delle parole dei nomi e cognomi devono essere maiuscole
        last_name = form.cleaned_data.get('last_name')
        words = last_name.split()
        capitalized_words = [word.capitalize() for word in words]
        tutor.user.last_name = ' '.join(capitalized_words)
        tutor.user.first_name = form.cleaned_data.get('first_name').capitalize()

        tutor.bio = form.cleaned_data.get('bio')
        tutor.profile_picture = form.cleaned_data.get('profile_picture')
        tutor.price_per_hour = form.cleaned_data.get('price_per_hour')

        if form.cleaned_data.get('new_location'):
            new_location = form.cleaned_data.get('new_location').title()
            location, created = Location.objects.get_or_create(name=new_location)
        else:
            location = form.cleaned_data.get('location')
        tutor.location = location

        subjects_list = list(form.cleaned_data.get('subjects'))
        if form.cleaned_data.get('new_subjects'):
            new_subjects = form.cleaned_data.get('new_subjects').split(',')
            for subject_name in new_subjects:
                subject_name = subject_name.strip()
                if subject_name:
                    # Le prime lettere delle parole delle materie devono essere maiuscole
                    words = subject_name.split()
                    capitalized_words = [word.capitalize() if word not in ["e", "E"] else word for word in words]
                    subject_name = ' '.join(capitalized_words)
                    subject, created = Subject.objects.get_or_create(name=subject_name)
                    subjects_list.append(subject)
        tutor.subjects.set(subjects_list)
        tutor.user.save()
        tutor.save()
        messages.success(self.request, 'Account aggiornato con successo!')
        send_profile_changes(tutor.user)
        return redirect('users:tutor_profile_detail')
