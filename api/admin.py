from django.contrib import admin
from .models import Address, Role, User, Question, Answer, Choice, Resource, Level, Program, Student, Mentor

# Register your models here
admin.site.register(Address)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Choice)
admin.site.register(Resource)
admin.site.register(Level)
admin.site.register(Program)
admin.site.register(Student)
admin.site.register(Mentor)