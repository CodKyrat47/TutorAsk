from django.urls import path
from .views import *

app_name = 'reviews'

urlpatterns = [
    path('tutor/<int:pk>/', TutorReviewView.as_view(), name='tutor_reviews'),
    path('student/<int:pk>/', StudentReviewView.as_view(), name='student_reviews'),
    path('review/<int:pk>/<int:is_like>/', vote_review, name='vote_review'),
    path('review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='delete_review'),
    path('review/<int:pk>/update/', ReviewUpdateView.as_view(), name='review_update')
]
