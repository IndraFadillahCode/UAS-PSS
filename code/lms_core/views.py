from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import (
    Course, CourseMember, CourseContent, Comment,
    CourseContentCompletion, CourseCompletion, CourseAnnouncement
)
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json


# Halaman Sederhana

def index(request):
    return HttpResponse("Hello, world. You're at the lms_core index.")

def testing(request):
    return render(request, 'testing.html')

def addData(request):
    return HttpResponse("Halaman Tambah Data")

def editData(request):
    return HttpResponse("Halaman Ubah Data")

def deleteData(request):
    return HttpResponse("Halaman Hapus Data")

# Fitur: Sertifikat Penyelesaian Kursus

def render_certificate(request, completion_id: int):
    course_completion = get_object_or_404(CourseCompletion, id=completion_id)

    if not request.user.is_authenticated or (request.user != course_completion.user and not request.user.is_staff):
        return HttpResponse("Tidak diizinkan untuk melihat sertifikat ini.", status=403)

    user = course_completion.user
    course = course_completion.course
    is_course_completed = True
    completion_date = course_completion.completion_date

    total_contents_in_course = CourseContent.objects.filter(course=course).count()
    completed_contents_by_user = CourseContentCompletion.objects.filter(
        user=user,
        content__course=course
    ).count()

    context = {
        'user': user,
        'course': course,
        'completion_date': completion_date,
        'certificate_id': course_completion.id,
        'is_course_completed': is_course_completed,
        'total_contents': total_contents_in_course,
        'completed_contents': completed_contents_by_user,
    }
    return render(request, 'certificate.html', context)

# Fitur: Statistik Aktivitas Pengguna

@login_required
def user_activity_stats(request):
    user = request.user

    data = {
        "courses_as_student": CourseMember.objects.filter(user=user).count(),
        "courses_created": Course.objects.filter(teacher=user).count(),
        "comments_written": Comment.objects.filter(member__user=user).count(),
        "contents_completed": CourseContentCompletion.objects.filter(user=user).count(),
    }

    return JsonResponse(data)


# Fitur: Moderasi Komentar oleh Teacher

@csrf_exempt
@login_required
def moderate_comment(request, comment_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comment not found"}, status=404)

    if comment.content.course.teacher != request.user and not request.user.is_superuser:
        return JsonResponse({"error": "Only the course teacher can moderate."}, status=403)

    try:
        data = json.loads(request.body)
        comment.is_moderated = data.get("is_moderated", True)
        comment.save()
        return JsonResponse({"message": "Komentar berhasil dimoderasi."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Fitur: Menampilkan komentar yang sudah dimoderasi

@login_required
def get_moderated_comments(request, content_id):
    comments = Comment.objects.filter(content_id=content_id, is_moderated=True)
    data = [
        {
            "id": c.id,
            "user": c.member.user.username,
            "comment": c.comment,
            "created_at": c.created_at
        }
        for c in comments
    ]
    return JsonResponse({"comments": data})


# Fitur: Course Announcements

@csrf_exempt
@login_required
def create_announcement(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher and not request.user.is_superuser:
        return JsonResponse({"error": "Only the course teacher can create announcement."}, status=403)

    try:
        data = json.loads(request.body)
        title = data.get("title")
        message = data.get("message")
        show_date = data.get("show_date")
        ann = CourseAnnouncement.objects.create(
            course=course,
            title=title,
            message=message,
            show_date=show_date
        )
        return JsonResponse({"message": "Announcement created.", "id": ann.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def list_announcements(request, course_id):
    anns = CourseAnnouncement.objects.filter(course_id=course_id).order_by('show_date')
    data = [
        {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "show_date": a.show_date
        }
        for a in anns
    ]
    return JsonResponse({"announcements": data})


@csrf_exempt
@login_required
def edit_announcement(request, announcement_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        ann = CourseAnnouncement.objects.get(pk=announcement_id)
    except CourseAnnouncement.DoesNotExist:
        return JsonResponse({"error": "Announcement not found"}, status=404)

    if request.user != ann.course.teacher and not request.user.is_superuser:
        return JsonResponse({"error": "Only the course teacher can edit announcement."}, status=403)

    try:
        data = json.loads(request.body)
        ann.title = data.get("title", ann.title)
        ann.message = data.get("message", ann.message)
        ann.show_date = data.get("show_date", ann.show_date)
        ann.save()
        return JsonResponse({"message": "Announcement updated."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@login_required
def delete_announcement(request, announcement_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        ann = CourseAnnouncement.objects.get(pk=announcement_id)
    except CourseAnnouncement.DoesNotExist:
        return JsonResponse({"error": "Announcement not found"}, status=404)

    if request.user != ann.course.teacher and not request.user.is_superuser:
        return JsonResponse({"error": "Only the course teacher can delete announcement."}, status=403)

    ann.delete()
    return JsonResponse({"message": "Announcement deleted."})


# Fitur: Content Completion Tracking

@csrf_exempt
@login_required
def add_completion(request, content_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        content = CourseContent.objects.get(pk=content_id)
        CourseContentCompletion.objects.create(user=request.user, content=content)
        return JsonResponse({"message": "Completion added."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400 )


@login_required
def list_completions(request, course_id):
    completions = CourseContentCompletion.objects.filter(
        user=request.user,
        content__course_id=course_id
    ).select_related('content')

    data = [
        {
            "id": c.id,
            "content_id": c.content.id,
            "content_title": c.content.name,
            "completion_date": c.completion_date
        }
        for c in completions
    ]
    return JsonResponse({"completions": data})


@csrf_exempt
@login_required
def delete_completion(request, completion_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        completion = CourseContentCompletion.objects.get(pk=completion_id, user=request.user)
        completion.delete()
        return JsonResponse({"message": "Completion deleted."})
    except CourseContentCompletion.DoesNotExist:
        return JsonResponse({"error": "Completion not found"}, status=404)