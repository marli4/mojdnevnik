from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from .decorators import roles_required 
from .models import *
from .utils import getWeekStart
from datetime import timedelta
from datetime import datetime


User = get_user_model()

class MyLoginView(LoginView):
    template_name="login.html"
    authentication_form=MyLoginForm

@login_required
def profileview(request):
    if (request.user.role == User.Role.STUDENT):
        user = User.objects.select_related('group').get(
            pk=request.user.pk
        )
    else:
        user = request.user
    notifications = Notification.objects.filter(user=user)

    context = {
        "user":user,
        "notifications": notifications,
    }
    return render(request, "profile.html", context)

@login_required
@roles_required("student")
def diaryView(request, date):
    day=date
    weekStart = getWeekStart(day)
    nextWeekStart = weekStart + timedelta(weeks=1)
    prevWeekStart = weekStart - timedelta(weeks=1)

    weekLessons = Lesson.objects.filter(date__gte=weekStart, date__lt=(weekStart + timedelta(days=7)))

    context = {
        "weekLessons":weekLessons,
    }

    return render(request, "diary.html", context)