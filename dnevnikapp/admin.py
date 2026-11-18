from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительно",
            {"fields":("patronimic","role","group")}
        ),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "first_name",
                "last_name",
                "email",
                "password1",
                "password2",
            ),
        }),
        ("Дополнительно", {
            "fields": ("patronimic", "role", "group"),
        }),
    )


admin.site.register(ParentChild)
admin.site.register(Group)
admin.site.register(Subject)
admin.site.register(TeacherSubject)
admin.site.register(Major)
admin.site.register(Lesson)
admin.site.register(Grade)
admin.site.register(Absence)
admin.site.register(Notification)
admin.site.register(Hometask)