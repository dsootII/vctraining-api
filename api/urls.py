
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'levels', LevelViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'choices', ChoiceViewSet)
router.register(r'resources', ResourceViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'mentors', MentorViewSet)
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='email_verification'),

    # Media routes
    path('media/<str:image_path>', image_view, name='image_view'),
]