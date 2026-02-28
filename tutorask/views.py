from django.shortcuts import render
from users.models import *


def home(request):
    """Home view"""
    locations = Location.objects.all().order_by('name')
    subjects = Subject.objects.all().order_by('name')
    return render(request, template_name="home.html", context={"locations": locations, "subjects": subjects})
