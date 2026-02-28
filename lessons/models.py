from django.core.exceptions import ValidationError
from django.db import models
from users.models import Tutor, Student, Subject
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta


class Availability(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='tutor_availabilities')
    day = models.DateField()
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        verbose_name_plural = "Availabilities"
        # Un tutor non può avere più disponibilità nello stesso momento
        constraints = [
            models.UniqueConstraint(fields=['tutor', 'day', 'start', 'end'], name='unique_availability')
        ]

    def clean(self):
        # Controlla che le date delle lezioni siano corrette
        if self.day is None or self.start is None or self.end is None:
            raise ValidationError("I campi sono obbligatori")

        today = datetime.now().date()
        one_month_later = today + relativedelta(months=1)

        if self.day <= today or self.day >= one_month_later:
            raise ValidationError("Il giorno deve rientrare nel prossimo mese")

        if self.start >= self.end:
            raise ValidationError("L'orario d'inizio lezione deve precedere l'orario di fine lezione")

        min_start_time = time(8, 0)
        max_end_time = time(20, 0)

        if self.start < min_start_time or self.end > max_end_time:
            raise ValidationError("Le fascia oraria per le lezioni va dalle 8:00 alle 20:00")

        start_datetime = datetime.combine(self.day, self.start)
        end_datetime = datetime.combine(self.day, self.end)
        duration = end_datetime - start_datetime

        if duration > timedelta(hours=4):
            raise ValidationError("La durata della singola lezione non può superare le 4 ore.")

        if duration < timedelta(hours=1):
            raise ValidationError("La singola lezione non può durare meno di un'ora.")

    def __str__(self):
        return f"{self.tutor.user.username} IN {self.day} FROM {self.start} TO {self.end}"


class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_bookings')
    booked_for = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='bookings')
    booked_at = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Bookings"
        # ogni disponibilità ha un'unica prenotazione associata
        constraints = [
            models.UniqueConstraint(fields=['booked_for'], name='unique_availability_booking')
        ]

    def __str__(self):
        return f"{self.student.user.username} FOR {self.booked_for.tutor.user.username} IN {self.booked_for.day} FROM {self.booked_for.start} TO {self.booked_for.end}"
