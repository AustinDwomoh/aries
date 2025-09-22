from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Organization, OrganizationMember, OrganizationJoinRequest, OrganizationSocialLink, OrganizationReputation
from .serializers import (
    OrganizationSerializer, 
    OrganizationListSerializer,
    OrganizationMemberSerializer,
    OrganizationJoinRequestSerializer,
    OrganizationSocialLinkSerializer,
    OrganizationReputationSerializer
)
from users.models import Profile
import json


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    List all organizations or create a new organization.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization_type', 'country', 'is_verified']
    search_fields = ['name', 'tag', 'description', 'primary_game']
    ordering_fields = ['name', 'date_joined', 'is_verified']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrganizationSerializer
        return OrganizationListSerializer
    
    def perform_create(self, serializer):
        # Set the created_by field to the current user
        serializer.save(created_by=self.request.user)
        
        # Create organization reputation
        OrganizationReputation.objects.create(organization=serializer.instance)


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an organization.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_organization(request, pk):
    """
    Join an organization.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        user = request.user
        
        # Check if user is already a member
        if OrganizationMember.objects.filter(organization=organization, user=user).exists():
            return Response(
                {'message': 'You are already a member of this organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's already a pending request
        if OrganizationJoinRequest.objects.filter(organization=organization, user=user, status='pending').exists():
            return Response(
                {'message': 'You already have a pending request to join this organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create join request
        message = request.data.get('message', '')
        join_request = OrganizationJoinRequest.objects.create(
            organization=organization,
            user=user,
            message=message
        )
        
        return Response(
            {'message': 'Join request sent successfully.'},
            status=status.HTTP_201_CREATED
        )
        
    except Organization.DoesNotExist:
        return Response(
            {'message': 'Organization not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_organization(request, pk):
    """
    Leave an organization.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        user = request.user
        
        # Check if user is a member
        try:
            member = OrganizationMember.objects.get(organization=organization, user=user)
            member.delete()
            return Response(
                {'message': 'You have left the organization.'},
                status=status.HTTP_200_OK
            )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'message': 'You are not a member of this organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Organization.DoesNotExist:
        return Response(
            {'message': 'Organization not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def organization_members(request, pk):
    """
    Get all members of an organization.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        members = OrganizationMember.objects.filter(organization=organization, is_active=True)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Organization.DoesNotExist:
        return Response(
            {'message': 'Organization not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_member_role(request, pk, user_id):
    """
    Update a member's role in an organization.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        user = User.objects.get(pk=user_id)
        
        # Check if the requesting user is an admin of the organization
        try:
            requesting_member = OrganizationMember.objects.get(organization=organization, user=request.user)
            if requesting_member.role not in ['admin']:
                return Response(
                    {'message': 'You do not have permission to update member roles.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'message': 'You are not a member of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the member's role
        try:
            member = OrganizationMember.objects.get(organization=organization, user=user)
            new_role = request.data.get('role')
            if new_role in ['admin', 'captain', 'member', 'recruit']:
                member.role = new_role
                member.save()
                return Response(
                    {'message': f'Member role updated to {new_role}.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'Invalid role.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'message': 'User is not a member of this organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
    except Organization.DoesNotExist:
        return Response(
            {'message': 'Organization not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {'message': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_member(request, pk, user_id):
    """
    Remove a member from an organization.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        user = User.objects.get(pk=user_id)
        
        # Check if the requesting user is an admin of the organization
        try:
            requesting_member = OrganizationMember.objects.get(organization=organization, user=request.user)
            if requesting_member.role not in ['admin']:
                return Response(
                    {'message': 'You do not have permission to remove members.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'message': 'You are not a member of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Remove the member
        try:
            member = OrganizationMember.objects.get(organization=organization, user=user)
            member.delete()
            return Response(
                {'message': 'Member removed from organization.'},
                status=status.HTTP_200_OK
            )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'message': 'User is not a member of this organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
    except Organization.DoesNotExist:
        return Response(
            {'message': 'Organization not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {'message': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def organization_reputation(request, pk):
    """
    Get organization reputation.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        reputation, created = OrganizationReputation.objects.get_or_create(organization=organization)
        serializer = OrganizationReputationSerializer(reputation)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Organization.DoesNotExist:
        return Response(
            {'message': 'Organization not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_organization(request, pk):
    """
    Follow an organization.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        # Add follow logic here (if you have a follow system)
        # For now, just return success
        return Response({'success': True})
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_organization(request, pk):
    """
    Unfollow an organization.
    """
    try:
        organization = Organization.objects.get(pk=pk)
        # Add unfollow logic here (if you have a follow system)
        # For now, just return success
        return Response({'success': True})
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
