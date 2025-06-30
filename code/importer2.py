import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 3)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'simplelms.settings'
import django
django.setup()

import csv
import json
from random import randint
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from lms_core.models import Course, CourseMember, CourseContent, Comment

import time
start_time = time.time()

filepath = './csv_data/'

# Fungsi untuk memasukkan data dari CSV
# Ini bisa lebih rapi jika menggunakan fungsi terpisah untuk setiap jenis data,
# atau menggunakan Django management command.
# Namun, untuk saat ini, kita langsung perbaiki bagian encoding.

# Masukkan data user
try:
    with open(filepath + 'user-data.csv', 'r', encoding='utf-8') as csvfile: # <--- Perubahan di sini
        reader = csv.DictReader(csvfile)
        obj_create = []
        for num, row in enumerate(reader):
            if not User.objects.filter(username=row['username']).exists():
                obj_create.append(User(username=row['username'], 
                                        password=make_password(row['password']), 
                                        email=row['email'],
                                        first_name=row['firstname'],
                                        last_name=row['lastname']))
        User.objects.bulk_create(obj_create)
    print("User data inserted successfully.")
except FileNotFoundError:
    print("user-data.csv not found. Skipping user data import.")
except Exception as e:
    print(f"Error importing user data: {e}")

# Masukkan data course
try:
    with open(filepath + 'course-data.csv', 'r', encoding='utf-8') as csvfile: # <--- Perubahan di sini
        reader = csv.DictReader(csvfile)
        obj_create = []
        for num, row in enumerate(reader):
            if not Course.objects.filter(pk=num+1).exists():
                # Pastikan teacher yang diacu ada
                try:
                    teacher_user = User.objects.get(pk=int(row['teacher']))
                    obj_create.append(Course(name=row['name'], price=int(row['price']), # Pastikan price diubah ke int
                                            description=row['description'], 
                                            teacher=teacher_user))
                except User.DoesNotExist:
                    print(f"User with ID {row['teacher']} not found for course {row['name']}. Skipping.")
        Course.objects.bulk_create(obj_create)
    print("Course data inserted successfully.")
except FileNotFoundError:
    print("course-data.csv not found. Skipping course data import.")
except Exception as e:
    print(f"Error importing course data: {e}")

# Masukkan data member
try:
    with open(filepath + 'member-data.csv', 'r', encoding='utf-8') as csvfile: # <--- Perubahan di sini
        reader = csv.DictReader(csvfile)
        obj_create = []
        for num, row in enumerate(reader):
            if not CourseMember.objects.filter(pk=num+1).exists():
                try:
                    course_obj = Course.objects.get(pk=int(row['course_id']))
                    user_obj = User.objects.get(pk=int(row['user_id']))
                    obj_create.append(CourseMember(course_id=course_obj,
                                                    user_id=user_obj, 
                                                    roles=row['roles']))
                except (Course.DoesNotExist, User.DoesNotExist):
                    print(f"Course or User not found for member data {row}. Skipping.")
        CourseMember.objects.bulk_create(obj_create)
    print("Member data inserted successfully.")
except FileNotFoundError:
    print("member-data.csv not found. Skipping member data import.")
except Exception as e:
    print(f"Error importing member data: {e}")

# Masukkan data content (dari JSON)
try:
    with open(filepath + 'contents.json', 'r', encoding='utf-8') as jsonfile: # <--- Perubahan di sini
        contents_data = json.load(jsonfile)
        obj_create = []
        for num, row in enumerate(contents_data): # Ubah `comments` menjadi `contents_data` agar lebih jelas
            if not CourseContent.objects.filter(pk=num+1).exists():
                try:
                    course_obj = Course.objects.get(pk=int(row['course_id']))
                    obj_create.append(CourseContent(course_id=course_obj, 
                                                    video_url=row['video_url'], 
                                                    name=row['name'], 
                                                    description=row['description']))
                except Course.DoesNotExist:
                    print(f"Course with ID {row['course_id']} not found for content {row['name']}. Skipping.")
        CourseContent.objects.bulk_create(obj_create)
    print("Content data inserted successfully.")
except FileNotFoundError:
    print("contents.json not found. Skipping content data import.")
except Exception as e:
    print(f"Error importing content data: {e}")

# Masukkan data comment (dari JSON)
try:
    with open(filepath + 'comments.json', 'r', encoding='utf-8') as jsonfile: # <--- Perubahan di sini
        comments_data = json.load(jsonfile) # Ubah `comments` menjadi `comments_data`
        obj_create = []
        for num, row in enumerate(comments_data):
            if int(row['user_id']) > 50: # Logika ini mungkin perlu disesuaikan dengan ID user Anda yang sebenarnya
                row['user_id'] = randint(5, 40) # Pastikan user ID ini valid di database Anda
            
            # Cek apakah CourseMember ada sebelum membuat Comment
            try:
                # Cari CourseMember berdasarkan user_id dan content_id's course_id
                # Asumsi: comment.member_id merujuk ke CourseMember, bukan User langsung
                # Dapatkan content dulu untuk mengetahui course_id nya
                content_obj = CourseContent.objects.get(pk=int(row['content_id']))
                member_obj = CourseMember.objects.get(
                    course_id=content_obj.course_id,
                    user_id=User.objects.get(pk=int(row['user_id']))
                )
                
                if not Comment.objects.filter(pk=num+1).exists():
                    obj_create.append(Comment(content_id=content_obj, 
                                            member_id=member_obj, # Pastikan ini objek CourseMember
                                            comment=row['comment']))
            except (CourseContent.DoesNotExist, CourseMember.DoesNotExist, User.DoesNotExist):
                print(f"Related content, member, or user not found for comment data {row}. Skipping.")
        Comment.objects.bulk_create(obj_create)
    print("Comment data inserted successfully.")
except FileNotFoundError:
    print("comments.json not found. Skipping comment data import.")
except Exception as e:
    print(f"Error importing comment data: {e}")

print("--- %s seconds ---" % (time.time() - start_time))