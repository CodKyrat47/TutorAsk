from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('signup/', user_signup, name='user_signup'),
    path('signup/student', StudentSignUpView.as_view(), name='student_signup'),
    path('signup/tutor', TutorSignUpView.as_view(), name='tutor_signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('student_profile/', StudentProfileView.as_view(), name='student_profile'),
    path('profile/delete/', delete_profile_confirm, name='delete_profile_confirm'),
    path('tutor_profile/', TutorProfileDetailView.as_view(), name='tutor_profile_detail'),
    path('tutor_profile/edit/', TutorProfileUpdateView.as_view(), name='tutor_profile_edit')
]
