from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import *
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .decorators import roles_required 
from .models import *
from .utils import getWeekStart
from datetime import timedelta
from django.db.models import Prefetch
from django.core.exceptions import PermissionDenied


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
    weekStart = getWeekStart(date)
    nextWeekStart = weekStart + timedelta(weeks=1)
    prevWeekStart = weekStart - timedelta(weeks=1)

    weekLessons = Lesson.objects.select_related("subject", "teacher"
                                                ).prefetch_related(
                                                    Prefetch(
                                                        "grades",
                                                        queryset=Grade.objects.filter(student=request.user),
                                                        to_attr="student_grades"
                                                    ),
                                                    Prefetch(
                                                        "absences",
                                                        queryset=Absence.objects.filter(student=request.user),
                                                        to_attr="student_absences"
                                                    )
                                                ).filter(date__gte=weekStart, date__lt=(weekStart + timedelta(days=7)), group=request.user.group
                                                ).order_by("date","lesson_number")    
    
    days = {str(i): {"lessons": [None] * 8, "date": weekStart + timedelta(i)} for i in range(7)}
    for lesson in weekLessons:
        lesson.grade = lesson.student_grades[0] if lesson.student_grades else None
        lesson.absence = lesson.student_absences[0] if lesson.student_absences else None
        
        daynum = (lesson.date - weekStart).days
        days[str(daynum)]["lessons"][lesson.lesson_number-1] = lesson

    context = {
        "days":days,
        "prevWeekStart":prevWeekStart,
        "nextWeekStart":nextWeekStart,
        "weeknum":date.isocalendar().week,
    }
    return render(request, "diary.html", context)

@login_required
@roles_required("teacher","admin")
def groupListView(request):
    groupslist = Group.objects.all().order_by("name")
    context = {
        "groups":groupslist,
    }
    return render(request, "grouplist.html", context=context)

@login_required
@roles_required("teacher")
def lessonsView(request, date):
    weekStart = getWeekStart(date)
    nextWeekStart = weekStart + timedelta(weeks=1)
    prevWeekStart = weekStart - timedelta(weeks=1)

    weekLessons = Lesson.objects.select_related("subject", "group"
                                                ).filter(date__gte=weekStart, date__lt=(weekStart + timedelta(days=7)), teacher=request.user
                                                ).order_by("date","lesson_number")
    
    days = {str(i): {"lessons": [None] * 8, "date": weekStart + timedelta(i)} for i in range(7)}
    for lesson in weekLessons:
        daynum = (lesson.date - weekStart).days
        days[str(daynum)]["lessons"][lesson.lesson_number-1] = lesson

    context = {
        "days":days,
        "prevWeekStart":prevWeekStart,
        "nextWeekStart":nextWeekStart,
        "weeknum":date.isocalendar().week,
    }
    return render(request, "lessons.html", context=context)

@login_required
def groupSubjectsView(request, groupid):
    if request.user.role == User.Role.STUDENT:
        if groupid != request.user.group.id:
            raise PermissionDenied

    subjects = Subject.objects.all()
    context={
        "subjects":subjects,
        "group":Group.objects.filter(pk=groupid).first(),
    }
    return render(request, "subjectslist.html", context=context)

@login_required
def gradeBookView(request, groupid, subjectid):
    if request.user.role == User.Role.STUDENT:
        if groupid != request.user.group.id:
            raise PermissionDenied
    return render(request, "gradebook.html")