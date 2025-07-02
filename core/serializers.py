from rest_framework import serializers
from .models import CustomUser, Post, Comment, Likes, Message, PrivateChat
from django.contrib.auth.hashers import make_password


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'created_at', 'updated_at', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        user = super().create(validated_data)
        return user


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post 
        depth = 1
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ['user', 'post']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class PrivateChatSerializer(serializers.ModelSerializer):
    class Meta:
        model: PrivateChat
        fields = '__all__'