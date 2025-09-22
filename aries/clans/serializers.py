from rest_framework import serializers
from .models import Clan, ClanStats, ClanMember, ClanSocialLink, ClanJoinRequest
from users.serializers import UserSerializer


class ClanSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClanSocialLink
        fields = ['id', 'link_type', 'url']
        read_only_fields = ['id']


class ClanStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClanStats
        fields = '__all__'
        read_only_fields = ['id']


class ClanMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ClanMember
        fields = ['id', 'clan', 'user', 'role', 'joined_at', 'is_active']
        read_only_fields = ['id', 'joined_at']


class ClanJoinRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ClanJoinRequest
        fields = ['id', 'clan', 'user', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class ClanSerializer(serializers.ModelSerializer):
    stats = ClanStatsSerializer(read_only=True)
    social_links = ClanSocialLinkSerializer(many=True, read_only=True)
    clan_members = ClanMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = Clan
        fields = [
            'id', 'username', 'name', 'tag', 'description', 'profile_picture',
            'logo', 'website', 'country', 'primary_game', 'stats', 'social_links',
            'clan_members', 'date_joined', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']
