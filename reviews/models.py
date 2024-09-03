from django.db import models
from users.models import Tutor, Student
from django.core.exceptions import ValidationError


class Review(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='tutor_reviews')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Reviews"
        # Uno studente può scrivere una sola recensione per tutor
        unique_together = ('tutor', 'student')

    @property
    def helpful_count(self):
        """Conta i like delle recensioni"""
        return self.votes.filter(is_like=True).count()

    @property
    def useless_count(self):
        """Conta i dislike delle recensioni"""
        return self.votes.filter(is_like=False).count()

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError('La valutazione deve essere compresa tra 1 e 5.')
        super().clean()

    def __str__(self):
        return f"{self.student.user.username} TO {self.tutor.user.username}"


class ReviewVote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='votes')
    is_like = models.BooleanField()

    class Meta:
        verbose_name_plural = "ReviewVotes"
        # Uno studente può lasciare solo un like/dislike per recensione
        unique_together = ('review', 'student')

    def __str__(self):
        like_text = "Like" if self.is_like else "Dislike"
        return f"{self.student.user.username} FOR {self.review} WITH {like_text}"
