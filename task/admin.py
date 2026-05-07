from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Task, Worker, TaskType, Position

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "deadline", "priority", "task_type", "is_completed",]
    search_fields = ["name",]
    list_filter = ["priority", "is_completed",]


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ["name",]
    search_fields = ["name",]


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ["name",]
    search_fields = ["name",]


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position",)
    fieldsets = UserAdmin.fieldsets + (("Position info", {"fields": ("position",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Position info", {"fields": ("position",)}),)
