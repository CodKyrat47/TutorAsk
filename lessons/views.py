from django.views.generic import ListView, DetailView, UpdateView, CreateView
from .templatetags.custom_tags import build_paginated_url
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import *
from reviews.models import *
from .models import *
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.db.models import OuterRef, Subquery, Count, IntegerField, Q, Exists, Value, Avg, Case, When
from django.db.models.functions import Coalesce
from django.core.mail import send_mail
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
import threading
from datetime import datetime
from django.utils.html import strip_tags
from .forms import *


def send_booking_mail(booking, mail_subject, student_mail_action, tutor_mail_action):
    """Invia una mail di prenotazione effettuata sia allo studente che al tutor"""
    def send_mail_task(subj, student_obj, tutor_obj, source, student_recipient, tutor_recipient):
        try:
            send_mail(subj, strip_tags(student_obj), source, student_recipient, html_message=student_obj)
            send_mail(subj, strip_tags(tutor_obj), source, tutor_recipient, html_message=tutor_obj)
        except Exception as e:
            print(f"Errore durante l'invio dell'email: {e}")

    subject = mail_subject
    formatted_date = booking.booked_for.day.strftime('%d/%m/%Y')
    formatted_start = booking.booked_for.start.strftime('%H:%M')
    formatted_end = booking.booked_for.end.strftime('%H:%M')
    student_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #d4eaf7; border-radius: 5px; background-color: #f0f8ff;">
                <h3>Salve {booking.student.user.get_full_name()},</h3>
                <p>{student_mail_action}</p>
                <p><strong>Tutor:</strong> {booking.booked_for.tutor.user.get_full_name()}</p>
                <p><strong>Data:</strong> {formatted_date}</p>
                <p><strong>Orario:</strong> {formatted_start} - {formatted_end}</p>
                <p><strong>Materia:</strong> {booking.subject}</p>
                <p>Speriamo di rivederti presto!</p>
                <p>Il team di TutorAsk</p>
                <hr style="border: none; border-top: 1px solid #d4eaf7;">
                <p style="font-size: 12px; color: #555;">Questa è una email automatica, per favore non rispondere.</p>
            </div>
        </body>
        </html>
        '''
    tutor_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #d4eaf7; border-radius: 5px; background-color: #f0f8ff;">
                <h3>Salve {booking.booked_for.tutor.user.get_full_name()},</h3>
                <p>{tutor_mail_action}</p>
                <p><strong>Studente:</strong> {booking.student.user.get_full_name()}</p>
                <p><strong>Data:</strong> {formatted_date}</p>
                <p><strong>Orario:</strong> {formatted_start} - {formatted_end}</p>
                <p><strong>Materia:</strong> {booking.subject}</p>
                <p>A presto!</p>
                <p>Il team di TutorAsk</p>
                <hr style="border: none; border-top: 1px solid #d4eaf7;">
                <p style="font-size: 12px; color: #555;">Questa è una email automatica, per favore non rispondere.</p>
            </div>
        </body>
        </html>
        '''
    email_from = 'noreply.tutorask2024@gmail.com'
    student_recipient_list = [booking.student.user.email]
    tutor_recipient_list = [booking.booked_for.tutor.user.email]

    thread = threading.Thread(target=send_mail_task, args=(subject, student_message, tutor_message, email_from, student_recipient_list, tutor_recipient_list))
    thread.start()


def send_availability_mail(availability, mail_subject, action):
    """Invia una mail realtiva alla disponibilità (crezione, modifica ed eliminazione)"""
    def send_mail_task(subj, obj, source, recipient):
        try:
            send_mail(subj, strip_tags(obj), source, recipient, html_message=obj)
        except Exception as e:
            print(f"Errore durante l'invio dell'email: {e}")

    subject = mail_subject
    formatted_date = availability.day.strftime('%d/%m/%Y')
    formatted_start = availability.start.strftime('%H:%M')
    formatted_end = availability.end.strftime('%H:%M')
    if action == "Elimination":
        message = f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #d4eaf7; border-radius: 5px; background-color: #f0f8ff;">
                    <h3>Salve {availability.tutor.user.get_full_name()},</h3>
                    <p>la tua disponibilità è stata cancellata come da te richiesto.</p>
                    <p><strong>Data:</strong> {formatted_date}</p>
                    <p><strong>Orario:</strong> {formatted_start} - {formatted_end}</p>
                    <p>A presto!</p>
                    <p>Il team di TutorAsk</p>
                    <hr style="border: none; border-top: 1px solid #d4eaf7;">
                    <p style="font-size: 12px; color: #555;">Questa è una email automatica, per favore non rispondere.</p>
                </div>
            </body>
            </html>
            '''
    elif action == "Edit":
        message = f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #d4eaf7; border-radius: 5px; background-color: #f0f8ff;">
                    <h3>Salve {availability.tutor.user.get_full_name()},</h3>
                    <p>la tua disponibilità è stata modificata come da te richiesto.</p>
                    <p>Di seguito è riportata la disponibilità aggiornata</p>
                    <p><strong>Data:</strong> {formatted_date}</p>
                    <p><strong>Orario:</strong> {formatted_start} - {formatted_end}</p>
                    <p>A presto!</p>
                    <p>Il team di TutorAsk</p>
                    <hr style="border: none; border-top: 1px solid #d4eaf7;">
                    <p style="font-size: 12px; color: #555;">Questa è una email automatica, per favore non rispondere.</p>
                </div>
            </body>
            </html>
            '''
    else:  # action == "Addition"
        message = f'''
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #d4eaf7; border-radius: 5px; background-color: #f0f8ff;">
                            <h3>Salve {availability.tutor.user.get_full_name()},</h3>
                            <p>la tua disponibilità è stata aggiunta con successo.</p>
                            <p><strong>Data:</strong> {formatted_date}</p>
                            <p><strong>Orario:</strong> {formatted_start} - {formatted_end}</p>
                            <p>A presto!</p>
                            <p>Il team di TutorAsk</p>
                            <hr style="border: none; border-top: 1px solid #d4eaf7;">
                            <p style="font-size: 12px; color: #555;">Questa è una email automatica, per favore non rispondere.</p>
                        </div>
                    </body>
                    </html>
                    '''
    email_from = 'noreply.tutorask2024@gmail.com'
    recipient_list = [availability.tutor.user.email]

    thread = threading.Thread(target=send_mail_task, args=(subject, message, email_from, recipient_list))
    thread.start()


def recommend_tutors_for_student(user):
    """Ordina i tutor in base all'esperienza dello studente loggato"""
    # Raccoglie i dati delle prenotazioni dello studente
    booked_subjects = Booking.objects.filter(student__user=user).values_list('subject__name', flat=True)
    booked_subjects = set(booked_subjects)  # Rimuove i duplicati

    # Raccoglie i tutor che hanno avuto una recensione alta dallo studente
    student_reviews = Review.objects.filter(student__user=user)
    preferred_tutors = {review.tutor.pk: review.rating for review in student_reviews if review.rating >= 4}

    # Calcola il prezzo medio tra tutti i tutor
    average_price = Tutor.objects.aggregate(Avg('price_per_hour'))['price_per_hour__avg']

    tutors = Tutor.objects.all()
    recommendations = []

    for tutor in tutors:
        score = 0

        # Punti per materie corrispondenti
        tutor_subjects = set(tutor.subjects.all().values_list('name', flat=True))
        common_subjects = booked_subjects & tutor_subjects
        score += len(common_subjects) * 2

        # Punti per recensioni positive
        if tutor.pk in preferred_tutors:
            score += 3

        # Punti se il prezzo è al di sotto della media
        if tutor.price_per_hour <= average_price:
            score += 1

        recommendations.append((tutor, score))

    # Ordina i tutor per punteggio decrescente
    recommendations.sort(key=lambda x: x[1], reverse=True)

    return recommendations


class TutorListView(ListView):
    """View che mostra tutti i tutor"""
    model = Tutor
    template_name = 'lessons/tutor_list.html'
    context_object_name = 'tutors'
    paginate_by = 5  # Numero di tutor mostrati per pagina

    def get_queryset(self):
        current_date = datetime.now().date()

        # Costruisce il profilo dello studente se autenticato
        if self.request.user.is_authenticated and self.request.user.is_student:
            recommended = recommend_tutors_for_student(self.request.user)
        else:
            recommended = []

        # Subquery per trovare le disponibilità future non prenotate per ogni tutor
        available_availabilities_subquery = Availability.objects.filter(
            tutor=OuterRef('pk'),
            day__gt=current_date,
            bookings__isnull=True
        ).values('tutor')

        # Conteggio delle disponibilità future non prenotate e annotamento sia del numero sia della loro esistenza
        available_availabilities_count_subquery = available_availabilities_subquery.annotate(count=Count('id')).values('count')
        queryset = Tutor.objects.annotate(
            available_availabilities_count=Coalesce(
                Subquery(available_availabilities_count_subquery, output_field=IntegerField()), 0
            ),
            has_availabilities=Exists(available_availabilities_subquery)
        )

        # Recupera i parametri di ricerca
        location = self.request.GET.get('location', '')
        subject = self.request.GET.get('subject', '')
        min_rating = self.request.GET.get('min_rating', '')
        max_price = self.request.GET.get('max_price', '')
        day = self.request.GET.get('exact_day', '')

        # Applica i filtri solo se specificati
        is_search = location or subject or min_rating or max_price or day
        if is_search:
            if location:
                queryset = queryset.filter(location__name__iexact=location)
            if subject:
                queryset = queryset.filter(subjects__name__iexact=subject)
            if min_rating:
                queryset = queryset.filter(rating__gte=int(min_rating))
            if max_price:
                queryset = queryset.filter(price_per_hour__lte=int(max_price))
            if day:
                selected_day = datetime.strptime(day, '%Y-%m-%d').date()
                if selected_day > current_date:
                    queryset = queryset.filter(tutor_availabilities__day=selected_day, tutor_availabilities__bookings__isnull=True)
                else:
                    queryset = queryset.none()
            queryset = queryset.annotate(relevance=Value(0, output_field=IntegerField()))
        elif recommended:
            # Condizione per assegnare lo score relativo al tutor
            conditions = [
                When(pk=tutor.pk, then=Value(score))
                for tutor, score in recommended
            ]

            queryset = queryset.annotate(
                relevance=Case(
                    *conditions,
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        else:
            queryset = queryset.annotate(relevance=Value(0, output_field=IntegerField()))

        if self.request.user.is_authenticated and self.request.user.is_tutor:
            # Escludi il tutor corrente dal queryset
            queryset = queryset.exclude(pk=self.request.user.tutor.pk)

        # Ordinamento
        queryset = queryset.order_by('-relevance', '-has_availabilities', '-rating', 'price_per_hour',
                                     'user__first_name', 'user__last_name')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.all().order_by('name')
        context['location'] = self.request.GET.get('location', '')
        context['subjects'] = Subject.objects.all().order_by('name')
        context['subject'] = self.request.GET.get('subject', '')
        context['min_rating'] = self.request.GET.get('min_rating', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['exact_day'] = self.request.GET.get('exact_day', '')
        context['build_paginated_url'] = build_paginated_url
        return context


class TutorDetailView(LoginRequiredMixin, DetailView):
    """View per un tutor in particolare"""
    model = Tutor
    template_name = 'lessons/tutor_detail.html'
    context_object_name = 'tutor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutor = self.get_object()
        current_date = datetime.now().date()

        # Recupera le disponibilità del tutor dal giorno successivo a quello odierno
        # e le prenotazioni ricevute
        all_availabilities = Availability.objects.filter(tutor=tutor, day__gt=current_date)
        booked_availabilities_subquery = Booking.objects.filter(
            booked_for=OuterRef('pk')
        ).values('booked_for')

        # Esclude le disponibilità soggette a prenotazione
        available_availabilities = all_availabilities.exclude(
            id__in=Subquery(booked_availabilities_subquery)
        )

        context['available_availabilities'] = available_availabilities
        return context

    def post(self, request, *args, **kwargs):
        tutor = self.get_object()
        availability_id = request.POST.get('availability')
        subject_id = request.POST.get('subject')

        availability = get_object_or_404(Availability, id=availability_id, tutor=tutor)
        subject = get_object_or_404(Subject, id=subject_id)

        booking = Booking(student=request.user.student,
                          booked_for=availability,
                          subject=subject)
        booking.save()

        messages.success(request, 'La prenotazione è avvenuta con successo!')
        send_booking_mail(booking, mail_subject="Prenotazione lezione", student_mail_action="la tua prenotazione è avvenuta con successo.",
                          tutor_mail_action="uno studente ha appena prenotato una lezione con lei.")

        return redirect(self.request.path_info)


class BookingDeleteView(DeleteView):
    """View per l'eliminazione di una prenotazione"""
    model = Booking
    template_name = 'lessons/booking_confirm_delete.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_student:
            return reverse_lazy('users:student_profile')
        else:
            return reverse_lazy('lessons:tutor_dashboard')

    # Accesso riservato al tutor e allo studente coinvolti
    def dispatch(self, request, *args, **kwargs):
        right_student = request.user.is_authenticated and request.user.is_student and self.get_object().student == request.user.student
        right_tutor = request.user.is_authenticated and request.user.is_tutor and self.get_object().booked_for.tutor == request.user.tutor
        if not right_student and not right_tutor:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        booking = self.get_object()
        if self.request.user.is_student:
            send_booking_mail(booking, mail_subject="Eliminazione lezione",
                              student_mail_action="la tua prenotazione è stata cancellata come da te desiderato.",
                              tutor_mail_action="uno studente ha appena cancellato una prenotazione.")
        elif self.request.user.is_tutor:
            send_booking_mail(booking, mail_subject="Eliminazione lezione",
                              tutor_mail_action="la tua lezione è stata cancellata come da te desiderato.",
                              student_mail_action="il tutor ha appena cancellato una tua prenotazione.")
        messages.success(self.request, 'Prenotazione eliminata con successo!')
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Errore durante l\'eliminazione della prenotazione.')
        return response


class AvailabilityDeleteView(DeleteView):
    """View per l'eliminazione della disponibilità"""
    model = Availability
    template_name = 'lessons/availability_confirm_delete.html'
    success_url = reverse_lazy('lessons:tutor_dashboard')

    # Accesso riservato al tutor
    def dispatch(self, request, *args, **kwargs):
        right_tutor = request.user.is_authenticated and request.user.is_tutor and self.get_object().tutor == request.user.tutor
        if not right_tutor:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        availability = self.get_object()
        messages.success(self.request, 'Disponibilità eliminata con successo!')
        send_availability_mail(availability, mail_subject="Eliminazione disponibilità", action="Elimination")
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Errore durante l\'eliminazione della disponibilità.')
        return response


class AvailabilityUpdateView(UpdateView):
    """View per la modifica della disponibilità"""
    model = Availability
    form_class = AvailabilityForm
    template_name = 'lessons/availability_form.html'
    success_url = reverse_lazy('lessons:tutor_dashboard')

    # Accesso riservato al tutor
    def dispatch(self, request, *args, **kwargs):
        right_tutor = request.user.is_authenticated and request.user.is_tutor and request.user == self.get_object().tutor.user
        if not right_tutor:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Aggiunge il tutor alle kwargs del form"""
        kwargs = super().get_form_kwargs()
        kwargs['tutor'] = Tutor.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.tutor = Tutor.objects.get(user=self.request.user)
        availability = form.instance
        response = super().form_valid(form)
        messages.success(self.request, 'Disponibilità creata con successo!')
        send_availability_mail(availability, mail_subject="Creazione disponibilità", action="Addition")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Modifica disponibilità"
        return context


class AvailabilityCreateView(CreateView):
    """View per la creazione di una disponibilità"""
    model = Availability
    form_class = AvailabilityForm
    template_name = 'lessons/availability_form.html'
    success_url = reverse_lazy('lessons:tutor_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_tutor:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Aggiunge il tutor alle kwargs del form"""
        kwargs = super().get_form_kwargs()
        kwargs['tutor'] = Tutor.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.tutor = Tutor.objects.get(user=self.request.user)
        availability = form.instance
        response = super().form_valid(form)
        messages.success(self.request, 'Disponibilità creata con successo!')
        send_availability_mail(availability, mail_subject="Creazione disponibilità", action="Addition")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Creazione disponibilità"
        return context


def tutor_dashboard(request):
    """View per la gestione delle lezioni da parte di un tutor"""
    if not request.user.is_authenticated or not request.user.is_tutor:
        return render(request, 'not_authenticated.html', {"message": "Non hai i permessi per accedere a questa pagina."})

    tutor = Tutor.objects.get(user=request.user)
    now = datetime.now()

    # Recupero delle prenotazioni passate
    past_bookings = Booking.objects.filter(
        Q(booked_for__day__lt=now.date()) |
        Q(booked_for__day=now.date(), booked_for__start__lt=now.time())
    ).filter(booked_for__tutor=tutor).order_by('-booked_for__day', '-booked_for__start', '-booked_for__end')

    # Recupero delle prenotazioni future
    future_bookings = Booking.objects.filter(
        Q(booked_for__day__gt=now.date()) |
        Q(booked_for__day=now.date(), booked_for__start__gte=now.time())
    ).filter(booked_for__tutor=tutor).order_by('booked_for__day', 'booked_for__start', 'booked_for__end')

    # Recupero delle disponibilità passate
    past_availabilities = Availability.objects.filter(
        Q(day__lt=now.date()) |
        Q(day=now.date(), start__lte=now.time())
    ).filter(tutor=tutor).values_list('id', flat=True)

    # Recupero di qualsiasi prenotazione
    all_bookings = past_bookings | future_bookings
    availability_ids = all_bookings.values_list('booked_for_id', flat=True).distinct()

    # Recupero delle disponibilità future
    future_availabilities = (Availability.objects.filter(tutor=tutor).
                             exclude(id__in=availability_ids).
                             exclude(id__in=past_availabilities).order_by('day', 'start', 'end'))

    context = {
        'tutor': tutor,
        'future_availabilities': future_availabilities,
        'past_bookings': past_bookings,
        'future_bookings': future_bookings,
    }
    return render(request, 'lessons/tutor_dashboard.html', context)
