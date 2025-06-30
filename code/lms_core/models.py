import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from .utils import get_current_timestamp
from django.db.models.signals import post_save
from django.dispatch import receiver


# =====================
# COURSE
# =====================
class Course(models.Model):
    name = models.CharField("Nama Kursus", max_length=255)
    description = models.TextField("Deskripsi")
    price = models.IntegerField("Harga")
    image = models.ImageField("Gambar", upload_to="course", blank=True, null=True)
    teacher = models.ForeignKey(User, verbose_name="Pengajar", on_delete=models.RESTRICT)
    max_students = models.IntegerField("Maksimal Siswa", null=True, blank=True)
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Data Mata Kuliah"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def is_member(self, user):
        return CourseMember.objects.filter(course=self, user=user).exists()



# =====================
# COURSE MEMBER
# =====================
ROLE_OPTIONS = [('std', "Siswa"), ('ast', "Asisten")]

class CourseMember(models.Model):
    course = models.ForeignKey(Course, verbose_name="matkul", on_delete=models.RESTRICT)
    user = models.ForeignKey(User, verbose_name="siswa", on_delete=models.RESTRICT)
    roles = models.CharField("peran", max_length=3, choices=ROLE_OPTIONS, default='std')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscriber Matkul"
        verbose_name_plural = "Subscriber Matkul"
        unique_together = ('course', 'user')

    def __str__(self):
        return f"{self.id} {self.course.name} : {self.user.username}"



# =====================
# COURSE CONTENT
# =====================
class CourseContent(models.Model):
    name = models.CharField("judul konten", max_length=200)
    description = models.TextField("deskripsi", default='-')
    video_url = models.CharField('URL Video', max_length=200, null=True, blank=True)
    file_attachment = models.FileField("File", null=True, blank=True)
    course = models.ForeignKey(Course, verbose_name="matkul", on_delete=models.RESTRICT)
    parent = models.ForeignKey("self", verbose_name="induk", on_delete=models.RESTRICT, null=True, blank=True)
    release_date = models.DateTimeField("Tanggal Rilis", null=True, blank=True)
    end_date = models.DateTimeField("Tanggal Berakhir", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konten Matkul"
        verbose_name_plural = "Konten Matkul"

    def __str__(self):
        return f'{self.course.name} {self.name}'



# =====================
# COMMENT
# =====================
class Comment(models.Model):
    content = models.ForeignKey(CourseContent, verbose_name="konten", on_delete=models.CASCADE)
    member = models.ForeignKey(CourseMember, verbose_name="pengguna", on_delete=models.CASCADE)
    comment = models.TextField('komentar')
    is_moderated = models.BooleanField("Sudah Dimoderasi", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"

    def __str__(self):
        return "Komen: " + self.member.user.username + " - " + self.comment



# =====================
# CONTENT COMPLETION
# =====================
class CourseContentCompletion(models.Model):
    user = models.ForeignKey(User, verbose_name="Pengguna", on_delete=models.CASCADE)
    content = models.ForeignKey(CourseContent, verbose_name="Konten Kursus", on_delete=models.CASCADE)
    completion_date = models.DateTimeField("Tanggal Selesai", auto_now_add=True)

    class Meta:
        verbose_name = "Penyelesaian Konten"
        verbose_name_plural = "Penyelesaian Konten"
        unique_together = ('user', 'content')

    def __str__(self):
        return f"{self.user.username} - {self.content.name} (Selesai pada {self.completion_date.strftime('%Y-%m-%d')})"



# =====================
# COURSE COMPLETION
# =====================
class CourseCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    completion_date = models.DateTimeField(default=get_current_timestamp)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-completion_date']

    def __str__(self):
        return f"{self.user.username} completed {self.course.name}"



# =====================
# ANNOUNCEMENT
# =====================
class CourseAnnouncement(models.Model):
    course = models.ForeignKey(Course, verbose_name="Mata Kuliah", on_delete=models.CASCADE)
    title = models.CharField("Judul", max_length=200)
    message = models.TextField("Pesan")
    show_date = models.DateField("Tanggal Tampil")
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Pengumuman Kursus"
        verbose_name_plural = "Pengumuman Kursus"
        ordering = ['show_date']

    def __str__(self):
        return f"{self.course.name} - {self.title} (Tampil pada {self.show_date})"



# =====================
# BOOKMARK
# =====================
class CourseContentBookmark(models.Model):
    user = models.ForeignKey(User, verbose_name="Pengguna", on_delete=models.CASCADE)
    content = models.ForeignKey(CourseContent, verbose_name="Konten Kursus", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} bookmark {self.content.name}"



# =====================
# FEEDBACK
# =====================
class CourseFeedback(models.Model):
    user = models.ForeignKey(User, verbose_name="Pengguna", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name="Kursus", on_delete=models.CASCADE)
    rating = models.IntegerField("Rating", default=5)
    comment = models.TextField("Komentar", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} feedback for {self.course.name}"