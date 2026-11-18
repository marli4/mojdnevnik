from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.forms import ValidationError

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        PARENT = "parent", "Parent"
        TEACHER = "teacher", "Teacher"
        ADMIN = "admin", "Admin"

    first_name=models.CharField(max_length=30, null=False, blank=False, verbose_name="Имя")
    last_name=models.CharField(max_length=30, null=False, blank=False, verbose_name="Фамилия")
    patronimic = models.CharField(max_length=30, null=True, blank=True, verbose_name="Отчество")
    role = models.TextField(choices=Role.choices, default=Role.STUDENT, null=True, blank=True, verbose_name="Роль")
    group = models.ForeignKey("Group", null=True, blank=True, verbose_name="Группа", default=None, on_delete=models.SET_NULL)
    subjects = models.ManyToManyField("Subject", through="TeacherSubject", verbose_name="Преподаваемые предметы", blank=True)
    parents = models.ManyToManyField("self", through="ParentChild", null=True, related_name="children", symmetrical=False, verbose_name="Родители", through_fields=("child","parent"))
    REQUIRED_FIELDS=["first_name", "last_name"]
    class Meta:
        verbose_name="Пользователь"
        verbose_name_plural="Пользователи"

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()

        if self.role and self.role == CustomUser.Role.TEACHER and self.group != None:
            raise ValidationError({
                "group": "Выбранный пользователь не является студентом."
            })

class ParentChild(models.Model):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Родитель", related_name="parent_links")
    child = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Ребенок", related_name="child_links")
    class Meta:
            verbose_name = "Связь родитель-ребенок"
            verbose_name_plural = "Связи родитель-ребенок"
            constraints = [
                models.UniqueConstraint(
                    fields=["parent", "child"], name="unique_parent_child"
                )
            ]

    def clean(self):
        super().clean()
        if self.parent.role != CustomUser.Role.PARENT:
            raise ValidationError(
            {"parent": "Выбранный пользователь должен иметь роль Родитель."}
        )
        if self.child.role != CustomUser.Role.STUDENT:
            raise ValidationError(
            {"child": "Выбранный пользователь должен иметь роль Студент."}
        )
        if self.parent == self.child:
            raise ValidationError("Пользователь не может быть родителем самому себе.")

    def __str__(self):
        return str(self.parent) + ' - ' + str(self.child)

class Group(models.Model):
    name = models.CharField(verbose_name="Название")
    course = models.PositiveSmallIntegerField(verbose_name="Курс")
    major = models.ForeignKey("Major", on_delete=models.CASCADE, verbose_name="Направление", related_name="groups")

    class Meta:
        verbose_name="Группа"
        verbose_name_plural="Группы"

    def __str__(self):
        return self.name

#Реализовал связь многие ко многим
class TeacherSubject(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Преподаватель")
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE, verbose_name="Предмет")

    def __str__(self):
        return str(self.teacher) + ' ' + str(self.subject)

    def clean(self):
        super().clean()

        if self.teacher and self.teacher.role != CustomUser.Role.TEACHER:
            raise ValidationError({
                "teacher": "Выбранный пользователь не является преподавателем."
            })

class Major(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название")

    class Meta:
        verbose_name="Направление"
        verbose_name_plural="Направления"

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название")
    teachers = models.ManyToManyField(CustomUser, through=TeacherSubject, blank=True)
    
    class Meta:
        verbose_name="Предмет"
        verbose_name_plural="Предметы"

    def __str__(self):
        return self.name

class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, verbose_name="Предмет", related_name="lessons")
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name="Преподаватель", related_name="lessons")
    date = models.DateField(default=timezone.now, verbose_name="Дата")
    lesson_number = models.PositiveSmallIntegerField(verbose_name="Номер пары")
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name="Группа", related_name="lessons")
    room = models.CharField(verbose_name="Кабинет")
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date","lesson_number","group"],
                name="unique_lesson_per_date_number_group"
            )
        ]
        models.CheckConstraint(
            condition=models.Q(lesson_number__gt=0),
            name="lesson_number_greater_than_zero"
        )
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
    
    def clean(self):
        super().clean()

        if self.teacher and self.teacher.role != CustomUser.Role.TEACHER:
            raise ValidationError({
                "teacher": "Выбранный пользователь не является преподавателем."
            })
        if self.lesson_number and self.lesson_number <= 0:
            raise ValidationError({
                "lesson_number": "Пара не может быть меньше 1"
            })

    def __str__(self):
        return str(self.subject) + ' ' + str(self.date) + ' ' + str(self.lesson_number)

class Grade(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Занятие", related_name="grades")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Студент", related_name="grades")
    grade = models.PositiveSmallIntegerField(verbose_name="Оценка")
    comment = models.CharField(max_length=150, null=True, blank=True, verbose_name="Комментарий")
    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=["lesson","student"],
                name="grade_per_lesson_and_student"
            )
        ]
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"

    def clean(self):
        super().clean()

        if self.student and self.student.role != CustomUser.Role.STUDENT:
            raise ValidationError({
                "student": "Выбранный пользователь не является студентом."
            })
        if self.student and self.lesson:
            if self.student.group != self.lesson.group:
                raise ValidationError({
                    "student": "Студент не состоит в группе, для которой проводится это занятие."
                })

    def __str__(self):
        return str(self.student) + ' ' + str(self.lesson) + ' ' + str(self.grade)

class Absence(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Занятие", related_name="absences")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Студент", related_name="absences")
    is_excused=models.BooleanField(default=False, verbose_name="Уважительная причина")
    reason=models.CharField(max_length=150, null=True, blank=True, verbose_name="Причина")
    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=["lesson","student"],
                name="absence_per_lesson_and_student"
            )
        ]
        verbose_name = "Пропуск"
        verbose_name_plural = "Пропуски"

    def clean(self):
        super().clean()

        if self.student and self.student.role != CustomUser.Role.STUDENT:
            raise ValidationError({
                "student": "Выбранный пользователь не является студентом."
            })
        if self.student and self.lesson:
            if self.student.group != self.lesson.group:
                raise ValidationError({
                    "student": "Студент не состоит в группе, для которой проводится это занятие."
                })

    def __str__(self):
        return str(self.student) + ' ' + str(self.lesson)

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="notifications")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    text = models.TextField(verbose_name="Текст")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return str(self.user) + ' ' + str(self.created_at)

class Hometask(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="hometask")
    text = models.TextField()

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
    def __str__(self):
        return "Домашнее задание " + str(self.lesson)