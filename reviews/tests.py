from django.test import TestCase
from .models import *
from lessons.models import *
from users.models import *
from datetime import date, time, timedelta


class ComputeScoresTest(TestCase):
    """Test per il calcolo del rating del tutor e della reputazione degli studenti"""
    def setUp(self):
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
        self.student1 = Student.objects.create(
            user=User.objects.create_user(
                username="studenttest1",
                email="student1@test.it",
                password="student1test123",
                first_name="Student1",
                last_name="Test",
                birth_date=date(2005, 8, 15),
                is_student=True,
            )
        )
        self.student2 = Student.objects.create(
            user=User.objects.create_user(
                username="studenttest2",
                email="student2@test.it",
                password="student2test123",
                first_name="Student2",
                last_name="Test",
                birth_date=date(2004, 6, 6),
                is_student=True,
            )
        )
        self.student3 = Student.objects.create(
            user=User.objects.create_user(
                username="studenttest3",
                email="student3@test.it",
                password="student3test123",
                first_name="Student3",
                last_name="Test",
                birth_date=date(2003, 12, 20),
                is_student=True,
            )
        )
        self.availability1 = Availability.objects.create(
            tutor=self.tutor, day=datetime.today() + timedelta(days=3), start=time(15, 30), end=time(17, 00))
        self.availability2 = Availability.objects.create(
            tutor=self.tutor, day=datetime.today() + timedelta(days=5), start=time(10, 00), end=time(12, 30))
        self.availability3 = Availability.objects.create(
            tutor=self.tutor, day=datetime.today() + timedelta(days=7), start=time(17, 00), end=time(18, 00))
        self.booking1 = Booking.objects.create(student=self.student1, booked_for=self.availability1, subject=self.subject)
        self.booking2 = Booking.objects.create(student=self.student2, booked_for=self.availability2, subject=self.subject)
        self.booking3 = Booking.objects.create(student=self.student3, booked_for=self.availability3, subject=self.subject)
        self.review1 = Review.objects.create(tutor=self.tutor, student=self.student1, rating=1)
        self.review2 = Review.objects.create(tutor=self.tutor, student=self.student2, rating=4)
        self.review3 = Review.objects.create(tutor=self.tutor, student=self.student3, rating=5)
        self.reviewvVote1 = ReviewVote.objects.create(review=self.review1, student=self.student2, is_like=False)
        self.reviewvVote2 = ReviewVote.objects.create(review=self.review1, student=self.student3, is_like=False)
        self.reviewvVote3 = ReviewVote.objects.create(review=self.review2, student=self.student1, is_like=True)
        self.reviewvVote4 = ReviewVote.objects.create(review=self.review2, student=self.student3, is_like=True)

    def test_computeScores(self):
        self.student1.update_reputation()
        self.student2.update_reputation()
        self.student3.update_reputation()
        self.tutor.update_average_rating()
        tutor_expected_score = 4.000
        students_expected_scores = {
            'student1': 20,   # 0 Like 2 Dislike
            'student2': 100,  # 2 Like 0 Dislike
            'student3': 60    # 0 Like 0 Dislike
        }
        tutor_calcolated_score = self.tutor.rating
        students_calcolated_scores = {
            'student1': self.student1.reputation_score,
            'student2': self.student2.reputation_score,
            'student3': self.student3.reputation_score
        }
        self.assertAlmostEqual(tutor_expected_score, tutor_calcolated_score, places=3)
        self.assertEqual(students_expected_scores, students_calcolated_scores)
