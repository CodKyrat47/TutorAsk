from django.test import TestCase, Client
from tutorask import settings
from .models import *
from users.models import *
from django.urls import reverse
from datetime import date, datetime, timedelta, time
from .forms import AvailabilityForm
from django.conf import settings


class AvailabilityCreationTests(TestCase):
    """Test per la creazione delle disponibilità da parte di un tutor considerando tutte le casistiche"""
    def setUp(self):
        self.client = Client()
        self.tutor = Tutor.objects.create(
            user=User.objects.create_user(
                username="tutortest",
                email="test@test.it",
                password="tutortest123",
                first_name="Tutor",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_tutor=True,
            ),
            bio="Tutor test per la creazione di availability",
            location=Location.objects.create(name="Modena"),
            price_per_hour=25
        )
        self.tutor.subjects.add(Subject.objects.create(name="TechWeb"))
        self.client.login(username='tutortest', password='tutortest123')
        self.url = reverse('lessons:availability_create')
        self.availability = Availability.objects.create(
            tutor=self.tutor, day=datetime.today()+timedelta(days=1), start=time(10, 0), end=time(12, 00))

    def test_right_availability(self):
        day = datetime.today() + timedelta(days=3)
        start = time(10, 0)
        end = time(12, 0)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertTrue(form.is_valid())

    def test_past_availability(self):
        day = datetime.today() - timedelta(days=3)
        start = time(10, 0)
        end = time(12, 0)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("Il giorno deve rientrare nel prossimo mese", form.errors['__all__'])

    def test_over_one_month_availability(self):
        day = datetime.today() + timedelta(days=35)
        start = time(10, 0)
        end = time(12, 0)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("Il giorno deve rientrare nel prossimo mese", form.errors['__all__'])

    def test_early_time_availability(self):
        day = datetime.today() + timedelta(days=6)
        start = time(7, 0)
        end = time(10, 0)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("Le fascia oraria per le lezioni va dalle 8:00 alle 20:00", form.errors['__all__'])

    def test_late_time_availability(self):
        day = datetime.today() + timedelta(days=6)
        start = time(20, 0)
        end = time(22, 0)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("Le fascia oraria per le lezioni va dalle 8:00 alle 20:00", form.errors['__all__'])

    def test_short_duration_availability(self):
        day = datetime.today() + timedelta(days=14)
        start = time(15, 0)
        end = time(15, 45)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("La singola lezione non può durare meno di un'ora.", form.errors['__all__'])

    def test_long_duration_availability(self):
        day = datetime.today() + timedelta(days=10)
        start = time(14, 0)
        end = time(18, 30)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("La durata della singola lezione non può superare le 4 ore.", form.errors['__all__'])

    def test_end_before_start_availability(self):
        day = datetime.today() + timedelta(days=20)
        start = time(16, 0)
        end = time(14, 30)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("L'orario d'inizio lezione deve precedere l'orario di fine lezione", form.errors['__all__'])

    def test_overlapping_availability(self):
        day = datetime.today() + timedelta(days=1)
        start = time(10, 0)
        end = time(12, 0)

        form_data = {
            'day': day.strftime('%Y-%m-%d'),
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("La disponibilità si sovrappone con un'altra disponibilità esistente.", form.errors['__all__'])

    def test_not_complete_availability(self):
        day = datetime.today() + timedelta(days=7)

        form_data = {
            'day': day.strftime('%Y-%m-%d')
        }

        form = AvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn("I campi sono obbligatori", form.errors['__all__'])


class BookingEliminationTests(TestCase):
    """Test per l'eliminazione di una prenotazione sia da parte di uno studente sia da parte di un tutor"""
    def setUp(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        settings.EMAIL_HOST = 'smtp.gmail.com'
        settings.EMAIL_PORT = 587
        settings.EMAIL_USE_TLS = True
        settings.EMAIL_HOST_USER = 'noreply.tutorask2024@gmail.com'
        settings.EMAIL_HOST_PASSWORD = 'ntgl zudw pvtz nsgg'

        self.client = Client()
        self.tutor = Tutor.objects.create(
            user=User.objects.create_user(
                username="tutortest",
                email="tutor@test.it",
                password="tutortest123",
                first_name="Tutor",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_tutor=True,
            ),
            bio="Tutor test per la creazione di availability",
            location=Location.objects.create(name="Modena"),
            price_per_hour=25
        )
        self.subject = Subject.objects.create(name="TechWeb")
        self.tutor.subjects.add(self.subject)
        self.student = Student.objects.create(
            user=User.objects.create_user(
                username="studenttest",
                email="student@test.it",
                password="studenttest123",
                first_name="Student",
                last_name="Test",
                birth_date=date(2007, 11, 20),
                is_student=True,
            )
        )
        self.availability = Availability.objects.create(
            tutor=self.tutor, day=datetime.today()+timedelta(days=5), start=time(15, 30), end=time(17, 00))
        self.booking = Booking.objects.create(student=self.student, booked_for=self.availability, subject=self.subject)
        self.url = reverse('lessons:booking_delete', kwargs={'pk': self.booking.pk})

    def test_elimination_from_tutor(self):
        self.client.login(username='tutortest', password='tutortest123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(pk=self.booking.pk).exists())

    def test_elimination_from_student(self):
        self.client.login(username='studenttest', password='studenttest123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(pk=self.booking.pk).exists())

    def test_elimination_without_permission(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Non hai i permessi per accedere a questa pagina.")
        self.assertTrue(Booking.objects.filter(pk=self.booking.pk).exists())
