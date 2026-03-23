from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN        = 'admin',        'Admin'
        HEAD_TEACHER = 'head_teacher', 'Head Teacher'
        DOS          = 'dos',          'Director of Studies (DOS)'
        DOD          = 'dod',          'Director of Discipline (DOD)'
        TEACHER      = 'teacher',      'Teacher'
        ANIMATEUR    = 'animateur',    'Animateur'
        ANIMATRICE   = 'animatrice',   'Animatrice'
        ACCOUNTANT   = 'accountant',   'Accountant'
        STUDENT      = 'student',      'Student'
        PARENT       = 'parent',       'Parent'
        PUBLIC       = 'public',       'Public / Visitor'

    username   = models.CharField(max_length=50, unique=True)
    email      = models.EmailField(unique=True)
    first_name = models.CharField(max_length=60)
    last_name  = models.CharField(max_length=60)
    role       = models.CharField(max_length=20, choices=Role.choices, default=Role.PUBLIC)
    phone      = models.CharField(max_length=20, blank=True)
    photo      = models.ImageField(upload_to='staff/photos/', blank=True, null=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_staff'
    )

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    objects = CustomUserManager()

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        ordering            = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_head_teacher(self):
        return self.role == self.Role.HEAD_TEACHER

    @property
    def is_dos(self):
        return self.role == self.Role.DOS

    @property
    def is_dod(self):
        return self.role == self.Role.DOD

    @property
    def is_animateur(self):
        return self.role in (self.Role.ANIMATEUR, self.Role.ANIMATRICE)

    @property
    def is_accountant(self):
        return self.role == self.Role.ACCOUNTANT

    @property
    def is_management(self):
        return self.role in (self.Role.ADMIN, self.Role.HEAD_TEACHER)

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
    
    @property
    def is_parent(self):
        return self.role == self.Role.PARENT
    
    @property
    def is_staff_member(self):
        return self.role not in (self.Role.PUBLIC, self.Role.STUDENT, self.Role.PARENT)


class StaffProfile(models.Model):
    user          = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    employee_id   = models.CharField(max_length=20, unique=True, blank=True)
    department    = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    date_joined   = models.DateField(null=True, blank=True)
    notes         = models.TextField(blank=True)

    def __str__(self):
        return f"Profile — {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last = StaffProfile.objects.order_by('id').last()
            next_id = (last.id + 1) if last else 1
            self.employee_id = f"RSS{next_id:04d}"
        super().save(*args, **kwargs)