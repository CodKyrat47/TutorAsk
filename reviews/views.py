from django.db import IntegrityError
from django.views.generic import DetailView, DeleteView
from django.views.generic.edit import FormMixin, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import *
from lessons.models import Booking
from .forms import ReviewForm
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q


class TutorReviewView(FormMixin, DetailView):
    """View per la visione delle recensioni su un tutor con possibilità di inserirne una"""
    model = Tutor
    template_name = 'reviews/tutor_reviews.html'
    context_object_name = 'tutor'
    form_class = ReviewForm

    def get_success_url(self):
        return reverse_lazy('reviews:tutor_reviews', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.tutor_reviews.all().order_by('-created_at')
        if self.request.user.is_authenticated and self.request.user.is_student:
            # Verifica se lo studente ha già avuto una lezione con il tutor e se gli ha già lasciato una recensione
            student = self.request.user.student
            now = datetime.now()

            has_past_booking = Booking.objects.filter(
                Q(booked_for__day__lt=now.date()) |
                Q(booked_for__day=now.date(), booked_for__end__lt=now.time())
            ).filter(student=student, booked_for__tutor=self.object).exists()

            has_review = Review.objects.filter(
                tutor=self.object,
                student=student
            ).exists()

            if has_past_booking and not has_review:
                context['form'] = self.get_form()
            elif not has_past_booking:
                context['form'] = None
                context['info'] = "Non puoi inserire recensioni per i tutor con i quali non hai ancora sostenuto lezioni"
            elif has_review:
                context['form'] = None
                context['info'] = "Puoi inserire un'unica recensione per tutor"

            # Prepara una lista di ID degli studenti che hanno votato "like" e "dislike" per ciascuna recensione
            context['user_likes'] = {
                review.id: list(review.votes.filter(is_like=True).values_list('student_id', flat=True))
                for review in context['reviews']
            }
            context['user_dislikes'] = {
                review.id: list(review.votes.filter(is_like=False).values_list('student_id', flat=True))
                for review in context['reviews']
            }
        else:
            context['form'] = 'tutor'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.tutor = self.object
            review.student = request.user.student
            try:
                review.save()
                messages.success(request, 'La tua recensione è stata aggiunta con successo!')
                # Aggiorna il rating del tutor
                self.object.update_average_rating()
            except IntegrityError:
                messages.info(request, 'Hai già inserito una recensione per questo tutor.')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class StudentReviewView(DetailView):
    """View per la visione delle recensioni lasciate da uno studente"""
    model = Student
    template_name = 'reviews/student_reviews.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.student_reviews.all().order_by('-created_at')

        # Prepara una lista di ID degli studenti che hanno votato "like" e "dislike" per ciascuna recensione
        context['user_likes'] = {
            review.id: list(review.votes.filter(is_like=True).values_list('student_id', flat=True))
            for review in context['reviews']
        }
        context['user_dislikes'] = {
            review.id: list(review.votes.filter(is_like=False).values_list('student_id', flat=True))
            for review in context['reviews']
        }

        return context


def check_vote(review, student, existing_vote, is_like):
    """Gestisce la singolarità del voto (like/dislike) relativo ad un commento"""
    if existing_vote:
        if existing_vote.is_like == is_like:
            existing_vote.delete()
        else:
            existing_vote.delete()
            ReviewVote.objects.create(review=review, student=student, is_like=is_like)
    else:
        ReviewVote.objects.create(review=review, student=student, is_like=is_like)


def vote_review(request, pk, is_like):
    """Gestisce l'applicazione del voto al commento"""
    review = get_object_or_404(Review, pk=pk)
    if not request.user.is_authenticated:
        messages.info(request, "Devi effettuare il login")
        return redirect(request.META.get('HTTP_REFERER'))
    if not request.user.is_student:
        role = "tutor" if request.user.is_tutor else "admin"
        messages.info(request, f"Non puoi votare in qualità di {role}")
        return redirect(request.META.get('HTTP_REFERER'))

    student = request.user.student

    # Verifica se lo studente ha già votato
    existing_vote = ReviewVote.objects.filter(review=review, student=student).first()

    if student == review.student:
        messages.info(request, "Non puoi votare la tua stessa recensione")
        return redirect(request.META.get('HTTP_REFERER'))

    is_like = bool(int(is_like))
    check_vote(review, student, existing_vote, is_like)

    # Aggiorna il rating del tutor e la reputazione dello studente
    review.student.update_reputation()
    review.tutor.update_average_rating()

    return redirect(request.META.get('HTTP_REFERER'))


class ReviewDeleteView(DeleteView):
    """View per l'eliminazione della recensione"""
    model = Review
    template_name = 'reviews/review_confirm_delete.html'
    context_object_name = 'review'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        self.next_url = request.GET.get('next')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.next_url:
            return self.next_url
        return reverse_lazy('reviews:tutor_reviews', kwargs={'pk': self.object.tutor.pk})  # url in caso di rimozione del parametro

    def get_queryset(self):
        return Review.objects.filter(student=self.request.user.student)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tutor.update_average_rating()
        self.object.student.update_reputation()
        messages.success(self.request, 'La tua recensione è stata eliminata con successo!')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Errore durante l\'eliminazione della recensione.')
        return response


class ReviewUpdateView(UpdateView):
    """View per la modifica di una recensione"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_update.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            error_message = "Non hai i permessi per accedere a questa pagina."
            return render(request, 'not_authenticated.html', {'message': error_message})
        self.next_url = request.GET.get('next')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.next_url:
            return self.next_url
        return reverse_lazy('reviews:tutor_reviews', kwargs={'pk': self.object.tutor.pk})  # url in caso di rimozione del parametro

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tutor.update_average_rating()
        messages.success(self.request, 'La tua recensione è stata aggiornata con successo!')
        return response
