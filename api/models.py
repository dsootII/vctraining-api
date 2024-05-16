from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models

from django.utils.translation import gettext_lazy as _ # Translate of strings

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country} - {self.postal_code}"

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    weight = models.IntegerField(default=0)  # You can adjust the default value as needed
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)

    # Resolving user permission related name conflicts
    # Modify the user_permissions field with related_name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='vc_users_permissions',  # Change to your desired related name
        related_query_name='vc_user_permission'
    )

    # Modify the groups field with related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='vc_users_groups',  # Change to your desired related name
        related_query_name='vc_user_group'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Level(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    goal_points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.name)

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice Question'),
        ('TF', 'True/False'),
        ('SA', 'Short Answer'),
        ('FIB', 'Fill in the Blanks'),
    ]
    title = models.CharField(max_length=200)  # Title field for the question
    text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPE_CHOICES)
    points = models.PositiveIntegerField(default=1)  # Points for the question
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.title)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return str(self.question)

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.question)

class Resource(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    TYPE_CHOICES = [
        ('VIDEO', 'Video'),
        ('ARTICLE', 'Article'),
        ('BOOK', 'Book'),
        ('OTHER', 'Other'),
    ]
    resource_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

class Program(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.name)

class Mentor(models.Model):
    code = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return str(self.user)

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, blank=True, null=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return str(self.user)

