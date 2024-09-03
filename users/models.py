from django.contrib.auth.models import AbstractUser
from django.db import models
# Per la delete dell'immagine al momento della rimozione del tutor
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

DEFAULT_IMAGE_FILENAME = "default/default_user.png"


class Subject(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Locations"

    def __str__(self):
        return self.name


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)
    birth_date = models.DateField()

    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    reputation_score = models.IntegerField(default=60)  # Da 20 a 100

    class Meta:
        verbose_name_plural = "Students"

    def update_reputation(self):
        """Gestione reputazione dello studente"""
        reviews = self.student_reviews.all()
        total_likes = sum(review.helpful_count for review in reviews)
        total_dislikes = sum(review.useless_count for review in reviews)

        if total_likes + total_dislikes > 0:
            self.reputation_score = int(20 + (total_likes / (total_likes + total_dislikes)) * 80)
        else:
            self.reputation_score = 60  # Valore neutro se non ci sono recensioni o like/dislike

        self.save()

    def __str__(self):
        return self.user.username


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.ImageField(upload_to='profile_imgs/', default='default/default_user.png')
    bio = models.TextField(blank=True, null=True)
    subjects = models.ManyToManyField(Subject)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    price_per_hour = models.IntegerField(default=15)
    rating = models.FloatField(default=3.0)  # da 1 a 5

    class Meta:
        verbose_name_plural = "Tutors"

    def update_average_rating(self):
        """Gestione rating del tutor pesato con la valutazione degli studenti"""
        reviews = self.tutor_reviews.all()
        if not reviews.exists():
            self.rating = 3.0
        else:
            total_weighted_rating = 0
            total_weight = 0
            for review in reviews:
                student = review.student
                reputation_score = student.reputation_score
                # Normalizzazione del reputation_score da 20-100 a 0.2-1.0
                normalized_reputation_score = reputation_score / 100
                weighted_rating = review.rating * normalized_reputation_score
                total_weighted_rating += weighted_rating
                total_weight += normalized_reputation_score
            self.rating = max(1.0, total_weighted_rating / total_weight)  # minimo 1
        self.save()

    def __str__(self):
        return self.user.username


@receiver(post_delete, sender=Tutor)
def delete_tutor_image(sender, instance, **kwargs):
    """Segnale per eliminare la foto profilo dopo la sua eliminazione"""
    # Verifica se c'è una foto del profilo
    if instance.profile_picture and instance.profile_picture.name != DEFAULT_IMAGE_FILENAME:
        # Costruisci il percorso del file
        file_path = instance.profile_picture.path
        # Controlla se il file esiste e poi elimina
        if os.path.isfile(file_path):
            os.remove(file_path)


@receiver(pre_save, sender=Tutor)
def delete_tutor_image_on_change(sender, instance, **kwargs):
    """Segnale per eliminare la vecchia foto profilo dopo la sua modifica"""
    if not instance.pk:
        # Se l'istanza è nuova, non fare nulla
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_image = old_instance.profile_picture
    new_image = instance.profile_picture
    # Controlla se l'immagine è stata cambiata e non è l'immagine di default
    if old_image and old_image != new_image and old_image.name != DEFAULT_IMAGE_FILENAME:
        file_path = old_image.path
        if os.path.isfile(file_path):
            os.remove(file_path)
