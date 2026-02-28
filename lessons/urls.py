from django.urls import path
from .views import *

app_name = 'lessons'

urlpatterns = [
    path('tutor_list/', TutorListView.as_view(), name='tutor_list'),
    path('tutor_detail/<int:pk>/', TutorDetailView.as_view(), name='tutor_detail'),
    path('tutor_dashboard/', tutor_dashboard, name='tutor_dashboard'),
    path('booking/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),
    path('availability/<int:pk>/delete/', AvailabilityDeleteView.as_view(), name='availability_delete'),
    path('availability/<int:pk>/edit/', AvailabilityUpdateView.as_view(), name='availability_edit'),
    path('availability/create/', AvailabilityCreateView.as_view(), name='availability_create')
]
