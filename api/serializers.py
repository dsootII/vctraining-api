from rest_framework import serializers
from .models import *

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address_serializer = AddressSerializer(data=address_data)
        
        if address_serializer.is_valid():
            address_instance = address_serializer.save()
            user_instance = User.objects.create(address=address_instance, **validated_data)
            return user_instance
        else:
            # Handle invalid address data
            raise serializers.ValidationError("Invalid address data")

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address')
        address_instance, _ = Address.objects.get_or_create(**address_data)

        # Retrieve all attributes from the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Replace address attribute with instance object
        instance.address = address_instance
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'birthdate', 'photo', 'email', 'role', 'address']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class MentorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Mentor
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_instance = user_serializer.save()
        else:
            raise serializers.ValidationError("Invalid user data")

        student = Student.objects.create(
            user=user_instance,
            **validated_data
        )
        return student

    class Meta:
        model = Student
        fields = '__all__'