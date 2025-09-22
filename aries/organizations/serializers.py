from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Organization, 
    OrganizationMember, 
    OrganizationJoinRequest, 
    OrganizationSocialLink, 
    OrganizationReputation
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login']


class OrganizationSocialLinkSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationSocialLink model."""
    class Meta:
        model = OrganizationSocialLink
        fields = ['id', 'link_type', 'url']


class OrganizationReputationSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationReputation model."""
    class Meta:
        model = OrganizationReputation
        fields = [
            'id', 'reputation_score', 'total_events_organized', 'total_participants_reached',
            'average_event_rating', 'total_prize_money_distributed', 'total_revenue_generated',
            'on_time_completion_rate', 'participant_satisfaction', 'dispute_resolution_rate',
            'achievements', 'badges', 'is_verified_organizer', 'verification_level'
        ]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationMember model."""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at', 'is_active']


class OrganizationListSerializer(serializers.ModelSerializer):
    """Serializer for listing organizations (lightweight)."""
    members_count = serializers.SerializerMethodField()
    reputation = OrganizationReputationSerializer(read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'tag', 'description', 'logo', 'profile_picture', 
            'website', 'date_joined', 'primary_game', 'other_games', 'country',
            'is_verified', 'organization_type', 'members_count', 'reputation',
            'can_host_tournaments', 'can_sponsor_events', 'can_manage_prizes', 'can_verify_teams',
            'total_tournaments_hosted', 'total_prize_money_distributed'
        ]
    
    def get_members_count(self, obj):
        return obj.members.filter(is_active=True).count()


class OrganizationSerializer(serializers.ModelSerializer):
    """Full serializer for Organization model."""
    created_by = UserSerializer(read_only=True)
    members = OrganizationMemberSerializer(many=True, read_only=True)
    social_links = OrganizationSocialLinkSerializer(many=True, read_only=True)
    reputation = OrganizationReputationSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'tag', 'email', 'description', 'logo', 'profile_picture',
            'website', 'date_joined', 'primary_game', 'other_games', 'country',
            'is_verified', 'created_by', 'organization_type', 'is_active', 'is_staff', 
            'members', 'social_links', 'reputation', 'members_count',
            'can_host_tournaments', 'can_sponsor_events', 'can_manage_prizes', 'can_verify_teams',
            'business_license', 'tax_id', 'contact_phone', 'established_date',
            'total_prize_money_distributed', 'total_tournaments_hosted', 'average_tournament_size'
        ]
        read_only_fields = ['created_by', 'date_joined', 'is_active', 'is_staff']
    
    def get_members_count(self, obj):
        return obj.members.filter(is_active=True).count()
    
    def validate_tag(self, value):
        """Validate that the tag is unique and not too long."""
        if len(value) > 10:
            raise serializers.ValidationError("Tag must be 10 characters or less.")
        return value
    
    def validate_email(self, value):
        """Validate that the email is unique."""
        if self.instance and self.instance.email == value:
            return value
        if Organization.objects.filter(email=value).exists():
            raise serializers.ValidationError("An organization with this email already exists.")
        return value


class OrganizationJoinRequestSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationJoinRequest model."""
    user = UserSerializer(read_only=True)
    organization = OrganizationListSerializer(read_only=True)
    
    class Meta:
        model = OrganizationJoinRequest
        fields = ['id', 'user', 'organization', 'status', 'message', 'requested_at']


class CreateOrganizationSerializer(serializers.ModelSerializer):
    """Serializer for creating a new organization."""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'name', 'tag', 'email', 'password', 'confirm_password', 'description',
            'website', 'primary_game', 'other_games', 'country', 'organization_type',
            'can_host_tournaments', 'can_sponsor_events', 'can_manage_prizes', 'can_verify_teams',
            'business_license', 'tax_id', 'contact_phone', 'established_date'
        ]
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def validate_email(self, value):
        """Validate that the email is unique."""
        if Organization.objects.filter(email=value).exists():
            raise serializers.ValidationError("An organization with this email already exists.")
        return value
    
    def validate_tag(self, value):
        """Validate that the tag is unique."""
        if Organization.objects.filter(tag=value).exists():
            raise serializers.ValidationError("An organization with this tag already exists.")
        return value
    
    def create(self, validated_data):
        """Create a new organization."""
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        organization = Organization.objects.create(**validated_data)
        organization.set_password(password)
        organization.save()
        
        # Create organization reputation
        OrganizationReputation.objects.create(organization=organization)
        
        return organization
