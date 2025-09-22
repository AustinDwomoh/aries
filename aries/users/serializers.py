from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, PlayerStats


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']


class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = '__all__'
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stats = PlayerStatsSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'profile_picture', 'role', 'is_organizer', 
            'phone', 'is_verified', 'clan', 'social_links', 'stats'
        ]
        read_only_fields = ['id', 'user']
