from datetime import datetime
from typing import Optional, List
from ninja import Schema
from pydantic import Field, ConfigDict

# =====================
# USER
# =====================
class UserRegisterIn(Schema):
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserOut(Schema):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str

class LoginIn(Schema):
    username: str
    password: str

# =====================
# COURSE
# =====================
class CourseSchemaIn(Schema):
    name: str
    description: str
    price: int
    max_students: Optional[int] = None

class CourseEnrollmentLimitIn(Schema):
    max_students: Optional[int] = None

class CourseSchemaOut(Schema):
    id: int
    name: str
    description: str
    price: int
    image: Optional[str]
    teacher: UserOut
    max_students: Optional[int]
    created_at: datetime
    updated_at: datetime

# =====================
# COURSE MEMBER
# =====================
class CourseMemberOut(Schema):
    id: int 
    course: CourseSchemaOut
    user: UserOut
    roles: str

# =====================
# CONTENT
# =====================
class CourseContentMini(Schema):
    id: int
    name: str
    description: str
    course: CourseSchemaOut
    release_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class CourseContentFull(Schema):
    id: int
    name: str
    description: str
    video_url: Optional[str]
    file_attachment: Optional[str]
    course: CourseSchemaOut
    release_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class CourseContentIn(Schema):
    name: str
    description: Optional[str] = '-'
    video_url: Optional[str] = None
    file_attachment: Optional[str] = None
    parent_id: Optional[int] = None
    release_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# =====================
# COMMENT
# =====================
class CourseCommentOut(Schema):
    id: int
    content: CourseContentMini
    member: CourseMemberOut
    comment: str
    is_moderated: bool
    created_at: datetime
    updated_at: datetime

class CourseCommentIn(Schema):
    comment: str

class CourseCommentModerationIn(Schema):
    is_moderated: bool

# =====================
# BATCH ENROLL
# =====================
class BatchEnrollIn(Schema):
    user_ids: List[int]

# =====================
# COMPLETION
# =====================
class CourseContentCompletionIn(Schema):
    content_id: int

class CourseContentCompletionOut(Schema):
    id: int
    user: UserOut
    content: CourseContentMini
    completion_date: datetime

    model_config = ConfigDict(from_attributes=True)

class CourseCompletionIn(Schema):
    course_id: int = Field(..., description="ID of the course being marked as completed.")

class CourseCompletionOut(Schema):
    id: int
    user_id: int
    course_id: int
    completion_date: datetime

    model_config = ConfigDict(from_attributes=True)

# =====================
# BOOKMARK
# =====================
class AnnouncementIn(Schema):
    title: str
    message: str
    show_date: datetime

class AnnouncementOut(Schema):
    id: int
    course_id: int
    title: str
    message: str
    show_date: datetime
    created_at: datetime
    updated_at: datetime

class BookmarkIn(Schema):
    content_id: int

class BookmarkOut(Schema):
    id: int
    content: CourseContentFull
    course: CourseSchemaOut
    created_at: datetime

# =====================
# FEEDBACK
# =====================
class FeedbackIn(Schema):
    course_id: int
    rating: int
    comment: str

class FeedbackOut(Schema):
    id: int
    user: UserOut
    course: CourseSchemaOut
    rating: int
    comment: str
    created_at: datetime
    updated_at: datetime