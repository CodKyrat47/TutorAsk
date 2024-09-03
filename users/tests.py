from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from .models import *
from datetime import date


class UserAuthenticationTests(TestCase):
    """Test per la registrazione, il login e il logout degli utenti"""
    def setUp(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        settings.EMAIL_HOST = 'smtp.gmail.com'
        settings.EMAIL_PORT = 587
        settings.EMAIL_USE_TLS = True
        settings.EMAIL_HOST_USER = 'noreply.tutorask2024@gmail.com'
        settings.EMAIL_HOST_PASSWORD = 'ntgl zudw pvtz nsgg'

    def test_student_signup_view(self):
        response = self.client.get(reverse('users:student_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/registration/student_signup.html')

    def test_tutor_signup_view(self):
        response = self.client.get(reverse('users:tutor_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/registration/tutor_signup.html')

    def test_student_registration(self):
        response = self.client.post(reverse('users:student_signup'), {
            'username': 'teststudent',
            'first_name': 'Student',
            'last_name': 'Test',
            'email': 'student@test.com',
            'birth_date': '11/04/2002',
            'password1': 'testpassword',
            'password2': 'testpassword',
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertTemplateUsed(response, 'users/registration/login.html')
        self.assertTrue(Student.objects.filter(user__username='teststudent').exists())

    def test_student_registration_age_error(self):
        response = self.client.post(reverse('users:student_signup'), {
            'username': 'teststudent',
            'first_name': 'Student',
            'last_name': 'Test',
            'email': 'student@test.com',
            'birth_date': '11/04/2012',
            'password1': 'testpassword',
            'password2': 'testpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Devi avere almeno 14 anni")
        self.assertFalse(Student.objects.filter(user__username='teststudent').exists())

    def test_student_registration_email_already_exists_error(self):
        Student.objects.create(
            user=User.objects.create_user(
                username="studenttest",
                email="test@test.it",
                password="studenttest123",
                first_name="Student",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_student=True,
            )
        )
        response = self.client.post(reverse('users:student_signup'), {
            'username': 'teststudent',
            'first_name': 'Student',
            'last_name': 'Test',
            'email': 'test@test.it',
            'birth_date': '11/04/2002',
            'password1': 'testpassword',
            'password2': 'testpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Questo indirizzo email è già stato utilizzato")
        self.assertFalse(Student.objects.filter(user__username='teststudent').exists())

    def test_student_login(self):
        Student.objects.create(
            user=User.objects.create_user(
                username="studenttest",
                email="test@test.it",
                password="studenttest123",
                first_name="Student",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_student=True,
            )
        )
        response = self.client.post(reverse('users:login'), {'username': 'studenttest', 'password': 'studenttest123'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'users/student_profile.html')

    def test_student_logout(self):
        Student.objects.create(
            user=User.objects.create_user(
                username="studenttest",
                email="test@test.it",
                password="studenttest123",
                first_name="Student",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_student=True,
            )
        )
        self.client.post(reverse('users:login'), {'username': 'studenttest', 'password': 'studenttest123'})
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'users/registration/logged_out.html')

    def test_admin_login(self):
        User.objects.create_superuser(username='admintest', email='admin@admin.com', password='passwordtest', birth_date=date(2002, 4, 11))
        response = self.client.post(reverse('users:login'), {'username': 'admintest', 'password': 'passwordtest'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertFalse(response.wsgi_request.user.is_student)
        self.assertFalse(response.wsgi_request.user.is_tutor)
        self.assertTemplateUsed(response, 'home.html')

    def test_admin_logout(self):
        User.objects.create_superuser(username='admintest', email='admin@admin.com', password='passwordtest', birth_date=date(2002, 4, 11))
        self.client.post(reverse('users:login'), {'username': 'admintest', 'password': 'passwordtest'})
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'users/registration/logged_out.html')

    def test_tutor_registration(self):
        response = self.client.post(reverse('users:tutor_signup'), {
            'username': 'testtutor',
            'first_name': 'Tutor',
            'last_name': 'Test',
            'email': 'tutor@test.com',
            'birth_date': '11/04/2002',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'new_location': 'Modena',
            'new_subjects': 'TechWeb',
            'price_per_hour': 20
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertTemplateUsed(response, 'users/registration/login.html')
        self.assertTrue(Tutor.objects.filter(user__username='testtutor').exists())

    def test_tutor_registration_age_error(self):
        response = self.client.post(reverse('users:tutor_signup'), {
            'username': 'testtutor',
            'first_name': 'Tutor',
            'last_name': 'Test',
            'email': 'tutor@test.com',
            'birth_date': '11/04/2008',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'new_location': 'Modena',
            'new_subjects': 'TechWeb',
            'price_per_hour': 20
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Devi essere maggiorenne (almeno 18 anni)")
        self.assertFalse(Tutor.objects.filter(user__username='testtutor').exists())

    def test_tutor_registration_email_already_exists_error(self):
        tutor = Tutor.objects.create(
            user=User.objects.create_user(
                username="tutortest",
                email="test@test.it",
                password="tutortest123",
                first_name="Tutor",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_tutor=True,
            ),
            location=Location.objects.create(name="Modena"),
            price_per_hour=25
        )
        tutor.subjects.add(Subject.objects.create(name="TechWeb"))
        response = self.client.post(reverse('users:tutor_signup'), {
            'username': 'testtutor',
            'first_name': 'Tutor',
            'last_name': 'Test',
            'email': 'test@test.it',
            'birth_date': '25/09/2003',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'new_location': 'Modena',
            'new_subjects': 'TechWeb',
            'price_per_hour': 20
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Questo indirizzo email è già stato utilizzato")
        self.assertFalse(Tutor.objects.filter(user__username='testtutor').exists())

    def test_tutor_login(self):
        tutor = Tutor.objects.create(
            user=User.objects.create_user(
                username="tutortest",
                email="test@test.it",
                password="tutortest123",
                first_name="Tutor",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_tutor=True,
            ),
            location=Location.objects.create(name="Modena"),
            price_per_hour=25
        )
        tutor.subjects.add(Subject.objects.create(name="TechWeb"))
        response = self.client.post(reverse('users:login'), {'username': 'tutortest', 'password': 'tutortest123'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'users/tutor_profile_detail.html')

    def test_tutor_logout(self):
        tutor = Tutor.objects.create(
            user=User.objects.create_user(
                username="tutortest",
                email="test@test.it",
                password="tutortest123",
                first_name="Tutor",
                last_name="Test",
                birth_date=date(2002, 4, 11),
                is_tutor=True,
            ),
            location=Location.objects.create(name="Modena"),
            price_per_hour=25
        )
        tutor.subjects.add(Subject.objects.create(name="TechWeb"))
        self.client.post(reverse('users:login'), {'username': 'tutortest', 'password': 'tutortest123'})
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(response, 'users/registration/logged_out.html')
