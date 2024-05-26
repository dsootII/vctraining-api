import os
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status, serializers
from .models import *
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
import string, random



class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)

        return Response(UserSerializer(user).data)
    
class SignupDropdowns (APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        all_mentors = Mentor.objects.all()
        all_programs = Program.objects.all()

        try:
            all_mentors_serialized = MentorSerializer(all_mentors, many=True)
            all_programs_serialized = ProgramSerializer(all_programs, many=True)
            
            return Response(
                {
                    "mentors": all_mentors_serialized.data, 
                    "programs": all_programs_serialized.data
                }
            )
        except Exception as e:
            print(f"error occured while serializing {e}")
            return Response(f"error occured while serializing {e}")
        

class SignUpView(APIView):
    print("signup view entered")
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        #attempting to save user
        try:
            #first creating an address entry
            address_data = request.data.get('address')
            
            try:
                address = Address.objects.create(
                    street=address_data['street'],
                    city=address_data['city'],
                    state=address_data['state'],
                    country=address_data['country'],
                    postal_code = address_data['postal_code']
                )
                if address:
                    address.save()
                    del request.data['address']
                    request.data['address'] = address.id
            except Exception as e:
                print(f'Error creating address: {e}')
                return Response(f"Error creating address, {e}")
            
            #now, equipped with the address, saving the user in the database
            serializer = UserSerializer(data=request.data)
            
            if serializer.is_valid():    
                try:
                    user = serializer.save()
                    #handle the case where it's signup for mentor:
                    #randomly generate the code
                    
                    #handle the case where it's signup for student:
                    #getting the mentor and program objects from db
                    p1 = Program.objects.get(pk=request.data['program'])
                    m1 = Mentor.objects.get(pk=request.data['mentor'])
                    #creating the user entry
                    student = Student.objects.create(user=user, program=p1, mentor=m1)
                    print(student)
                    if student:
                        login(request, user)
                        
                        # Generate JWT token
                        refresh = RefreshToken.for_user(user)
                        
                        return Response(
                            {
                                "msg": "student successfully created",
                                "student_data": StudentSerializer(student).data,
                                "refresh": str(refresh),
                                "access": str(refresh.access_token)
                            }, 
                            status=status.HTTP_201_CREATED
                        )
                except Exception as e:
                    print("error occured in saving from serializer: ", e)
                    return Response(f"Error occured while saving user, {e}")
                try:
                    self.send_verification_email(user)
                except Exception as e:
                    print(f'Error sending verification email: {e}')
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors)
        
        #handling any error    
        except Exception as e:
            print(f'Error in signup process: {e}\n', 'serializer.errors:\n', serializer.errors)
            return Response({"detail": "An error occurred during sign up."}, status=status.HTTP_200_OK)

    def send_verification_email(self, user):
        try:
            current_site = get_current_site(self.request)
            subject = 'Activate Your Account'
            message = render_to_string('verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Error in send_verification_email: {e}')

class SignupViewMentor(APIView):

    def post(self, request, *args, **kwargs):
        print("mentorsignup view entered")
        
        #create the user entry
        try:
            #first creating an address entry
            address_data = request.data.get('address')
            
            try:
                address = Address.objects.create(
                    street=address_data['street'],
                    city=address_data['city'],
                    state=address_data['state'],
                    country=address_data['country'],
                    postal_code = address_data['postal_code']
                )
                if address:
                    address.save()
                    del request.data['address']
                    request.data['address'] = address.id
            except Exception as e:
                print(f'Error creating address: {e}')
                return Response(f"Error creating address, {e}")
            
            #now, equipped with the address, saving the user in the database
            serializer = UserSerializer(data=request.data)
            
            if serializer.is_valid():    
                try:
                    user = serializer.save()

                    # create the mentor entry.
                    # just need a code, and user
                    characters = string.ascii_uppercase + string.digits
                    #generate random code
                    code = ''.join(random.choices(characters, k=6))
                    try:
                        mentor = Mentor.objects.create(user=user, code=code)
                        print("Mentor created, ", mentor)
                        mentor.save()
                    except Exception as e:
                        print(e)
                        return Response(f"error occured in creating mentor, {e}")

                except Exception as e:
                    return Response(f"Error creating address, {e}")
            else:
                print("Serializer is not valid. printing serializer.inital_data, ", serializer.initial_data)
                Response(f"Error occured in serializer: {serializer.initial_data}")
                
        except Exception as e:
            return Response(f"Error occured while saving, {e}")

class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email_verified = True
            user.save()
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

class MentorViewSet(viewsets.ModelViewSet):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

def image_view(request, image_path):
    # Define the full path to the image file
    image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)
    # Check if the file exists
    if os.path.exists(image_full_path):
        # Serve the image using FileResponse
        return FileResponse(open(image_full_path, 'rb'), content_type='image/jpeg')
    else:
        # Return a 404 error if the file doesn't exist
        raise Http404()