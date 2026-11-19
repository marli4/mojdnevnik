from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView
from .forms import *
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .decorators import roles_required 
from .models import *
from .utils import getWeekStart
from datetime import timedelta, date
from django.db import transaction
from django.db.models import Prefetch
from django.core.exceptions import PermissionDenied
from collections import defaultdict
import calendar
from django.urls import reverse


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
                                                ).filter(date__gte=weekStart, date__lt=(weekStart + timedelta(days=7)), group_id=request.user.group_id
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
        if groupid != request.user.group_id:
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

    if request.GET.get("month"):
        month = int(request.GET.get("month"))
    else:
        return redirect(reverse("gradebook", kwargs={"groupid":groupid, "subjectid":subjectid}) + "?month=9")
    year = timezone.localdate().year
    daysinmonth = calendar.monthrange(year,month)[1]
    days = [date(year, month, day) for day in range(1, daysinmonth+1)]
    startdate = days[0]
    enddate = days[-1]

    prevMonth = 12 if month == 1 else month - 1
    nextMonth = 1 if month == 12 else month + 1
        
    students = list(User.objects.filter(group_id=groupid).order_by("last_name"))
    grades = list(Grade.objects.select_related("student__group", "lesson__subject"
                            ).filter(student__group_id=groupid, lesson__subject_id=subjectid, lesson__date__gte=startdate, lesson__date__lte=enddate)
    )
    absences = list(Absence.objects.select_related("student__group", "lesson__subject"
                            ).filter(student__group_id=groupid, lesson__subject_id=subjectid, lesson__date__gte=startdate, lesson__date__lte=enddate)
    )
    if grades:
        group = grades[0].student.group
        subject = grades[0].lesson.subject
    else:
        group = get_object_or_404(Group, pk=groupid)
        subject = get_object_or_404(Subject, pk=subjectid)

    grades_matrix = defaultdict(lambda: defaultdict(list))
    for grade in grades:
        studentid = grade.student_id
        day = grade.lesson.date.day
        grades_matrix[studentid][day].append(grade)

    absences_matrix = defaultdict(lambda: defaultdict(list))
    for absence in absences:
        studentid = absence.student_id
        day = absence.lesson.date.day
        absences_matrix[studentid][day].append(absence)

    for student in students:
        student.gradesbyday = grades_matrix[student.pk]
        student.absencesbyday = absences_matrix[student.pk]

    context = {
        "group": group,
        "subject": subject,
        "students":students,
        "days":days,
        "startdate":startdate,
        "prevMonth":prevMonth,
        "nextMonth":nextMonth,
    }
    return render(request, "gradebook.html", context=context)

@login_required
@roles_required("teacher","admin", "student")
def lessonView(request, lessonid):
    lesson = Lesson.objects.select_related("subject", "group", "hometask"
                            ).prefetch_related(
                                Prefetch("group__students__grades", queryset=Grade.objects.filter(lesson_id=lessonid)), 
                                Prefetch("group__students__absences", queryset=Absence.objects.filter(lesson_id=lessonid)),
                            ).filter(pk=lessonid).first()
    
    if lesson == None:
        return redirect("profile")
    
    students = lesson.group.students.all()

    if request.method == "POST" and (request.user.role == "teacher" or request.user.role == "admin"):
        with transaction.atomic():
            hometasktext = request.POST.get("hometask", "")

            Hometask.objects.update_or_create(lesson=lesson, defaults={"text": hometasktext})

            for student in students:

                # Оценка
                grade_value = request.POST.get(f"grade_{student.pk}")

                if grade_value:
                    Grade.objects.update_or_create(
                        student=student,
                        lesson=lesson,
                        defaults={"grade": int(grade_value)}
                    )
                else:
                    Grade.objects.filter(
                        student=student,
                        lesson=lesson
                    ).delete()

                # Пропуск
                absence_value = request.POST.get(f"absence_{student.pk}")

                if absence_value:
                    Absence.objects.update_or_create(
                        student=student,
                        lesson=lesson,
                        defaults={
                            "is_excused": absence_value == "УП"
                        }
                    )
                else:
                    Absence.objects.filter(
                        student=student,
                        lesson=lesson
                    ).delete()
        return redirect("lessons", lessonid=lesson.pk)

    for student in students:
        student.grade = student.grades.first()
        student.absence = student.absences.first()
    context = {
        "lesson":lesson,
        "students":students,
    }
    
    return render(request, "lesson.html", context=context)