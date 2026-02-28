from users.models import *
from lessons.models import *
from reviews.models import *
from datetime import time, date, datetime, timedelta
import random


def erase_db():
    """Cancella il DB"""
    print("DB cleanup")
    User.objects.all().delete()
    Location.objects.all().delete()
    Subject.objects.all().delete()


def init_db():
    """Inizializza il DB"""
    print("DB initialization")

    # Crea città
    locations = ['Modena', 'Roma', 'Milano', 'Venezia', 'Firenze', 'Palermo', 'Bari', 'Foggia', 'Bologna', 'Torino',
                 'Napoli', 'Genova', 'Verona', 'Trieste', 'Ancona', 'Perugia', 'Aosta', 'Trento', 'Cagliari', 'Messina', 'Catania']
    for name in locations:
        loc = Location(name=name)
        loc.save()

    # Crea materie
    subjects = ['Inglese', 'Informatica', 'Matematica', 'Economia', 'Fisica', 'Algoritmi', 'Giurisprudenza', 'Marketing',
                'Sistemi e Reti', 'Sviluppo Web']
    for sub in subjects:
        obj = Subject(name=sub)
        obj.save()

    # Crea admin
    admin = User.objects.create_superuser(username='andrea', email='foo@foo.com', password='andrea', birth_date=date(2002, 4, 11))
    admin.save()

    def random_date_of_birth(start_age, end_age):
        """Genera una data di nascita casuale basata sull'età specificata"""
        today = datetime.today()
        start_date = today.replace(year=today.year - end_age)
        end_date = today.replace(year=today.year - start_age)
        return start_date + (end_date - start_date) * random.random()

    def random_tutor_price():
        """Genera un prezzo casuale per tutor"""
        return random.randint(15, 60)

    def random_subjects():
        """Seleziona una o più materie casualmente"""
        return random.sample(list(Subject.objects.all()), k=random.randint(1, 3))

    def random_location():
        """Seleziona una location casuale"""
        return random.choice(Location.objects.all())

    tutor_first_names = ['Alessandro', 'Giulia', 'Federico', 'Chiara', 'Lorenzo', 'Martina', 'Matteo', 'Francesca', 'Stefano', 'Elisa',
                         'Giovanni', 'Valentina', 'Giorgio', 'Silvia', 'Roberto', 'Simona', 'Francesco', 'Anna', 'Marco', 'Elena']
    tutor_last_names = ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi', 'Romano', 'Colombo', 'Ricci', 'Marino', 'Greco',
                        'Bruno', 'Gallo', 'Conti', 'De Luca', 'Costa', 'Giordano', 'Rizzo', 'Lombardi', 'Moretti', 'Barbieri']

    student_first_names = ['Andrea', 'Sara', 'Luca', 'Alessandra', 'Davide', 'Laura', 'Michele', 'Giorgia', 'Riccardo', 'Monica',
                           'Emanuele', 'Beatrice', 'Antonio', 'Eleonora', 'Gabriele', 'Federica', 'Nicola', 'Marta', 'Pietro', 'Alice']
    student_last_names = ['Leone', 'Fontana', 'Caruso', 'Mariani', 'Ferraro', 'Gatti', 'Pellegrini', 'Bianco', 'Martini', 'Montanari',
                          'Riva', 'Villa', 'Serra', 'Contini', 'Mancini', 'Cattaneo', 'Orlando', 'Pagano', 'Santoro', 'Sorrentino']

    # Crea tutor
    tutors = []
    for i in range(20):
        tutor = Tutor.objects.create(
            user=User.objects.create_user(
                username=f"tutor{i+1}",
                email=f"tutor{i+1}@tutor.com",
                password=f"tutor{i+1}",
                first_name=random.choice(tutor_first_names),
                last_name=random.choice(tutor_last_names),
                birth_date=random_date_of_birth(18, 70),
                is_tutor=True,
            ),
            bio=f"Sono un tutor esperto in {', '.join([sub.name for sub in random_subjects()])}.",
            location=random_location(),
            price_per_hour=random_tutor_price()
        )
        tutor.subjects.set(random_subjects())
        tutors.append(tutor)
    for t in tutors:
        t.save()

    # Crea studenti
    students = []
    for i in range(20):
        student = Student.objects.create(
            user=User.objects.create_user(
                username=f"student{i+1}",
                email=f"student{i+1}@student.com",
                password=f"student{i+1}",
                first_name=random.choice(student_first_names),
                last_name=random.choice(student_last_names),
                birth_date=random_date_of_birth(14, 70),
                is_student=True,
            )
        )
        students.append(student)
    for s in students:
        s.save()

    print("Tutors and students stored")


def store_availabilities():
    """Crea disponibilità"""
    today = datetime.today()

    for tutor in Tutor.objects.all():
        # Genera disponibilità future entro un mese dalla data odierna
        for _ in range(random.randint(1, 3)):
            future_day = today + timedelta(days=random.randint(1, 30))
            start_hour = random.randint(8, 17)  # Orario di inizio tra le 8 e le 17
            end_hour = start_hour + random.randint(1, 3)  # Sessioni di 1-3 ore
            availability = Availability.objects.create(
                tutor=tutor,
                day=future_day.date(),
                start=time(start_hour, 0),
                end=time(end_hour, 0)
            )
            availability.save()

        # Genera disponibilità passate fino a due mesi prima della data odierna
        for _ in range(random.randint(1, 2)):
            past_day = today - timedelta(days=random.randint(1, 60))
            start_hour = random.randint(8, 17)  # Orario di inizio tra le 8 e le 17
            end_hour = start_hour + random.randint(1, 3)  # Sessioni di 1-3 ore
            availability = Availability.objects.create(
                tutor=tutor,
                day=past_day.date(),
                start=time(start_hour, 0),
                end=time(end_hour, 0)
            )
            availability.save()

    # Crea prenotazioni per le disponibilità passate
    for student in Student.objects.all():
        # Ottieni disponibilità passate che non sono state prenotate
        past_availabilities = Availability.objects.filter(day__lt=today.date()).exclude(bookings__isnull=False)
        if not past_availabilities:
            continue

        for _ in range(random.randint(1, 2)):
            if not past_availabilities:
                break

            availability = random.choice(past_availabilities)
            past_availabilities = past_availabilities.exclude(id=availability.id)  # Escludi la disponibilità selezionata

            subject = random.choice(list(availability.tutor.subjects.all()))
            booking = Booking.objects.create(
                student=student,
                booked_for=availability,
                subject=subject
            )
            booking.save()

    print("Availabilities and bookings stored")


def create_reviews():
    """Crea recensioni"""
    # Crea recensioni per i tutor con cui lo studente ha avuto lezioni
    for student in Student.objects.all():
        # Trova i tutor con cui lo studente ha avuto lezioni
        tutors_with_bookings = Tutor.objects.filter(tutor_availabilities__bookings__student=student).distinct()
        for tutor in tutors_with_bookings:
            # Controlla se lo studente ha già recensito questo tutor
            if Review.objects.filter(student=student, tutor=tutor).exists():
                continue

            # Crea una recensione con un rating casuale tra 1 e 5 e un commento
            rating = random.randint(1, 5)
            comment = [
                "Pessima esperienza",
                "Non sono rimasto completamente soddisfatto.",
                "Buona esperienza, ma potrebbe migliorare.",
                "Ottimo tutor! Molto preparato.",
                "Perfetto! Consigliato a tutti."
            ]

            review = Review.objects.create(
                tutor=tutor,
                student=student,
                rating=rating,
                comment=comment[rating-1]
            )
            tutor.update_average_rating()
            review.save()
    print("Reviews stored")


def create_review_votes():
    """Crea i voti alle recensioni"""
    # Aggiunge voti alle recensioni, evitando che lo studente voti la propria recensione
    for review in Review.objects.all():
        # Trova tutti gli studenti che non sono l'autore della recensione
        other_students = Student.objects.exclude(pk=review.student.pk)
        for student in other_students:
            # Controlla se lo studente ha già votato questa recensione
            if ReviewVote.objects.filter(student=student, review=review).exists():
                continue

            # Aggiungi un voto positivo o negativo in modo casuale
            is_like = random.choice([True, False])
            review_vote = ReviewVote.objects.create(
                review=review,
                student=student,
                is_like=is_like
            )
            student.update_reputation()
            review.tutor.update_average_rating()
            review_vote.save()
    print("Review votes stored")
