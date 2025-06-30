from datetime import datetime, timedelta
from typing import List, Optional

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ninja import NinjaAPI, Path, Router
from ninja.errors import HttpError

from lms_core.models import (
    Comment, Course, CourseAnnouncement, CourseCompletion, CourseContent,
    CourseContentBookmark, CourseContentCompletion, CourseFeedback, CourseMember
)
from lms_core.schema import (
    AnnouncementIn, AnnouncementOut, BatchEnrollIn, BookmarkIn, BookmarkOut, CourseCommentIn,
    CourseCommentModerationIn, CourseCommentOut, CourseCompletionIn, CourseCompletionOut,
    CourseContentCompletionIn, CourseContentCompletionOut, CourseContentFull, CourseContentIn,
    CourseEnrollmentLimitIn, CourseMemberOut, CourseSchemaIn, CourseSchemaOut, FeedbackIn,
    FeedbackOut, LoginIn, UserOut, UserRegisterIn
)
from lms_core.utils import create_jwt_token, validate_password

apiv1 = NinjaAPI()

# =====================
# AUTHENTICATION
# =====================

# Register
@apiv1.post("/auth/register", response=UserOut)
def register_user(request, user_in: UserRegisterIn):
    if User.objects.filter(username=user_in.username).exists():
        raise HttpError(400, "Username sudah digunakan")
    if User.objects.filter(email=user_in.email).exists():
        raise HttpError(400, "Email sudah digunakan")

    hashed_password = make_password(user_in.password)
    user = User.objects.create(
        username=user_in.username,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        password=hashed_password
    )
    return user

# Login
@apiv1.post("/auth/login")
def login_user(request, data: LoginIn):
    user = authenticate(request, username=data.username, password=data.password)
    if user:
        login(request, user)
        token = create_jwt_token(user)
        return {"message": "Login successful", "token": token}
    else:
        raise HttpError(401, "Invalid credentials")

# =====================
# COURSE
# =====================

# Komentar
@apiv1.put("/comments/{comment_id}/moderate", response=CourseCommentOut)
def moderate_comment(request, comment_id: int, moderation_in: CourseCommentModerationIn):
    if not request.user.is_authenticated or not request.user.is_staff:
        raise HttpError(403, "Tidak diizinkan")
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_moderated = moderation_in.is_moderated
    comment.save()
    return comment

@apiv1.get("/courses/{course_id}/contents/{content_id}/comments", response=List[CourseCommentOut])
def get_content_comments(request, course_id: int, content_id: int):
    content = get_object_or_404(CourseContent, id=content_id, course_id=course_id)
    comments = Comment.objects.filter(content=content, is_moderated=True).order_by('-created_at')
    return comments

# Enroll siswa
@apiv1.post("/courses/{course_id}/batch-enroll")
def batch_enroll_students(request, course_id: int, enroll_data: BatchEnrollIn):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_authenticated or not (request.user == course.teacher):
        raise HttpError(403, "Hanya pengajar kursus")

    if course.max_students is not None:
        current_members_count = CourseMember.objects.filter(course=course).count()
        if current_members_count >= course.max_students:
            raise HttpError(400, "Kuota siswa penuh")

    enrolled_count = 0
    for user_id in enroll_data.user_ids:
        user = get_object_or_404(User, id=user_id)
        if not CourseMember.objects.filter(course=course, user=user).exists():
            CourseMember.objects.create(course=course, user=user, roles='std')
            enrolled_count += 1

    return {"message": f"{enrolled_count} siswa berhasil didaftarkan."}

# Aktivitas pengguna
@apiv1.get("/users/{user_id}/dashboard")
def get_user_activity_dashboard(request, user_id: int):
    if not request.user.is_authenticated or (request.user.id != user_id and not request.user.is_staff):
        raise HttpError(403, "Tidak diizinkan")
    user = get_object_or_404(User, id=user_id)
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "courses_as_student": CourseMember.objects.filter(user=user, roles='std').count(),
        "courses_created_as_teacher": Course.objects.filter(teacher=user).count(),
        "comments_written": Comment.objects.filter(member__user=user).count(),
        "content_completed": CourseContentCompletion.objects.filter(user=user).count(),
    }

# Analytics
@apiv1.get("/courses/{course_id}/analytics")
def get_course_analytics(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_authenticated or not (request.user == course.teacher or request.user.is_staff):
        raise HttpError(403, "Tidak diizinkan")
    feedback_count = CourseFeedback.objects.filter(course=course).count()
    return {
        "course_id": course.id,
        "course_name": course.name,
        "total_members": CourseMember.objects.filter(course=course).count(),
        "total_contents": CourseContent.objects.filter(course=course).count(),
        "total_comments": Comment.objects.filter(content__course=course, is_moderated=True).count(),
        "total_feedbacks": feedback_count,
    }

# =====================
# COMPLETION & CERTIFICATE
# =====================

# Completion
@apiv1.post("/contents/{content_id}/complete", response=CourseContentCompletionOut)
def mark_content_complete(request, content_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    content = get_object_or_404(CourseContent, id=content_id)
    if not CourseMember.objects.filter(course=content.course, user=request.user).exists():
        raise HttpError(403, "Bukan anggota kursus")
    completion, created = CourseContentCompletion.objects.get_or_create(user=request.user, content=content)
    if not created:
        raise HttpError(409, "Sudah ditandai")
    total = CourseContent.objects.filter(course=content.course).count()
    done = CourseContentCompletion.objects.filter(user=request.user, content__course=content.course).count()
    if total > 0 and done >= total:
        CourseCompletion.objects.get_or_create(user=request.user, course=content.course)
    return completion

@apiv1.get("/courses/{course_id}/certificate_data", response=Optional[CourseCompletionOut])
def get_course_certificate_data(request, course_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    course = get_object_or_404(Course, id=course_id)
    cert = CourseCompletion.objects.filter(user=request.user, course=course).first()
    if not cert:
        raise HttpError(404, "Belum selesai")
    return cert

@apiv1.get("/users/{user_id}/completed_courses_list", response=List[CourseCompletionOut])
def list_user_completed_courses(request, user_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    if request.user.id != user_id and not request.user.is_staff:
        raise HttpError(403, "Tidak diizinkan")
    user = get_object_or_404(User, id=user_id)
    return CourseCompletion.objects.filter(user=user)

# =====================
# COURSE
# =====================

@apiv1.get("/courses", response=List[CourseSchemaOut])
def get_courses(request):
    return Course.objects.all()

@apiv1.get("/courses/{course_id}", response=CourseSchemaOut)
def get_course_detail(request, course_id: int):
    return get_object_or_404(Course, id=course_id)

@apiv1.post("/courses", response=CourseSchemaOut)
def create_course(request, course_in: CourseSchemaIn):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    return Course.objects.create(
        name=course_in.name,
        description=course_in.description,
        price=course_in.price,
        teacher=request.user,
        max_students=course_in.max_students
    )

# =====================
# COURSE CONTENT
# =====================

@apiv1.get("/courses/{course_id}/contents", response=List[CourseContentFull])
def get_course_contents(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    contents = CourseContent.objects.filter(course=course).order_by('created_at')
    now = timezone.now()
    visible = []
    for c in contents:
        if request.user.is_authenticated and request.user.is_staff:
            visible.append(c)
        elif (c.release_date is None or c.release_date <= now) and (c.end_date is None or c.end_date >= now):
            visible.append(c)
    return visible

@apiv1.post("/courses/{course_id}/contents", response=CourseContentFull)
def create_course_content(request, course_id: int, content_in: CourseContentIn):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_authenticated or not (request.user == course.teacher or request.user.is_staff):
        raise HttpError(403, "Tidak diizinkan")
    parent = None
    if content_in.parent_id:
        parent = get_object_or_404(CourseContent, id=content_in.parent_id, course=course)
    return CourseContent.objects.create(
        name=content_in.name,
        description=content_in.description,
        video_url=content_in.video_url,
        file_attachment=content_in.file_attachment,
        course=course,
        parent=parent,
        release_date=content_in.release_date,
        end_date=content_in.end_date
    )

@apiv1.get("/courses/{course_id}/completions/", response=List[CourseCompletionOut])
def list_completions(request, course_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher and not request.user.is_staff:
        raise HttpError(403, "Hanya pengajar yang bisa melihat data ini")

    return CourseCompletion.objects.filter(course=course)

# =====================
# ANNOUNCEMENT
# =====================

@apiv1.post("/courses/{course_id}/announcements/", response=AnnouncementOut)
def create_announcement_api(request, course_id: int, data: AnnouncementIn):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_authenticated or (request.user != course.teacher and not request.user.is_superuser):
        raise HttpError(403, "Only the course teacher can create announcement.")
    ann = CourseAnnouncement.objects.create(
        course=course,
        title=data.title,
        message=data.message,
        show_date=data.show_date
    )
    return AnnouncementOut(
        id=ann.id,
        course_id=ann.course.id,
        title=ann.title,
        message=ann.message,
        show_date=ann.show_date,
        created_at=ann.created_at,
        updated_at=ann.updated_at
    )

@apiv1.get("/courses/{course_id}/announcements/", response=List[AnnouncementOut])
def list_announcements_api(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    anns = CourseAnnouncement.objects.filter(course=course).order_by('show_date')
    return [AnnouncementOut(
        id=a.id,
        course_id=a.course.id,
        title=a.title,
        message=a.message,
        show_date=a.show_date,
        created_at=a.created_at,
        updated_at=a.updated_at
    ) for a in anns]

@apiv1.put("/announcements/{announcement_id}/", response=AnnouncementOut)
def edit_announcement_api(request, announcement_id: int, data: AnnouncementIn):
    ann = get_object_or_404(CourseAnnouncement, id=announcement_id)
    if not request.user.is_authenticated or (request.user != ann.course.teacher and not request.user.is_superuser):
        raise HttpError(403, "Only the course teacher can edit announcement.")
    ann.title = data.title
    ann.message = data.message
    ann.show_date = data.show_date
    ann.save()
    return AnnouncementOut(
        id=ann.id,
        course_id=ann.course.id,
        title=ann.title,
        message=ann.message,
        show_date=ann.show_date,
        created_at=ann.created_at,
        updated_at=ann.updated_at
    )

@apiv1.delete("/announcements/{announcement_id}/")
def delete_announcement_api(request, announcement_id: int):
    ann = get_object_or_404(CourseAnnouncement, id=announcement_id)
    if not request.user.is_authenticated or (request.user != ann.course.teacher and not request.user.is_superuser):
        raise HttpError(403, "Only the course teacher can delete announcement.")
    ann.delete()
    return {"message": "Announcement deleted."}

# =====================
# BOOKMARK
# =====================

@apiv1.post("/bookmarks/", response=BookmarkOut)
def add_bookmark(request, data: BookmarkIn):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    content = get_object_or_404(CourseContent, id=data.content_id)
    bookmark, created = CourseContentBookmark.objects.get_or_create(user=request.user, content=content)
    return BookmarkOut(
        id=bookmark.id,
        content=content,
        course=content.course,
        created_at=bookmark.created_at
    )

@apiv1.get("/bookmarks/", response=List[BookmarkOut])
def list_bookmarks(request):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    bookmarks = CourseContentBookmark.objects.filter(user=request.user).select_related('content__course')
    return [
        BookmarkOut(
            id=b.id,
            content=b.content,
            course=b.content.course,
            created_at=b.created_at
        ) for b in bookmarks
    ]

@apiv1.delete("/bookmarks/{bookmark_id}/")
def delete_bookmark(request, bookmark_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    bookmark = get_object_or_404(CourseContentBookmark, id=bookmark_id, user=request.user)
    bookmark.delete()
    return {"message": "Bookmark deleted."}

# =====================
# FEEDBACK
# =====================

@apiv1.post("/feedbacks/", response=FeedbackOut)
def add_feedback(request, data: FeedbackIn):
    if not request.user.is_authenticated:
        raise HttpError(401, "Harus login")
    course = get_object_or_404(Course, id=data.course_id)
    feedback, created = CourseFeedback.objects.get_or_create(user=request.user, course=course)
    feedback.rating = data.rating
    feedback.comment = data.comment
    feedback.save()
    return FeedbackOut(
        id=feedback.id,
        user=request.user,
        course=course,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at
    )

@apiv1.get("/courses/{course_id}/feedbacks/", response=List[FeedbackOut])
def list_feedbacks(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    feedbacks = CourseFeedback.objects.filter(course=course).select_related('user', 'course')
    return [
        FeedbackOut(
            id=f.id,
            user=f.user,
            course=f.course,
            rating=f.rating,
            comment=f.comment,
            created_at=f.created_at,
            updated_at=f.updated_at
        ) for f in feedbacks
    ]

@apiv1.put("/feedbacks/{feedback_id}/", response=FeedbackOut)
def edit_feedback(request, feedback_id: int, data: FeedbackIn):
    feedback = get_object_or_404(CourseFeedback, id=feedback_id, user=request.user)
    feedback.rating = data.rating
    feedback.comment = data.comment
    feedback.save()
    return FeedbackOut(
        id=feedback.id,
        user=feedback.user,
        course=feedback.course,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at
    )

@apiv1.delete("/feedbacks/{feedback_id}/")
def delete_feedback(request, feedback_id: int):
    feedback = get_object_or_404(CourseFeedback, id=feedback_id, user=request.user)
    feedback.delete()
    return {"message": "Feedback deleted."}