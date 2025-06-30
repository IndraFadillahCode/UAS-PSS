from django.contrib import admin
from lms_core.models import (
    Course,
    CourseMember,
    CourseContent,
    Comment,
    CourseContentCompletion,
    CourseCompletion,
    CourseAnnouncement
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "description", "teacher", 'created_at']
    list_filter = ["teacher"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "description", "price", "image", "teacher", "created_at", "updated_at"]

@admin.register(CourseMember)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'user', 'roles', 'created_at']
    list_filter = ['roles', 'course']
    search_fields = ['user__username', 'course__name']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "content", "member", "comment", "is_moderated", "created_at"]
    list_filter = ["is_moderated"]
    search_fields = ["comment", "member__user__username", "content__name"]

@admin.register(CourseContentCompletion)
class CourseContentCompletionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "content", "completion_date"]
    list_filter = ["user"]
    search_fields = ["user__username", "content__name"]

@admin.register(CourseCompletion)
class CourseCompletionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "course", "completion_date"]
    list_filter = ["user", "course"]
    search_fields = ["user__username", "course__name"]

@admin.register(CourseAnnouncement)
class CourseAnnouncementAdmin(admin.ModelAdmin):
    list_display = ["id", "course", "title", "show_date", "created_at"]
    list_filter = ["course"]
    search_fields = ["title", "message"]