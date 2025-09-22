from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Clan, ClanMember, ClanJoinRequest, ClanSocialLink
from .serializers import ClanSerializer, ClanMemberSerializer, ClanJoinRequestSerializer
from users.models import Profile
from scripts.error_handle import ErrorHandler


class ClanListCreateAPIView(APIView):
    """
    List all clans or create a new clan.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        clans = Clan.objects.filter(is_active=True).order_by('-date_joined')
        
        # Apply filters
        search = request.query_params.get('search')
        country = request.query_params.get('country')
        primary_game = request.query_params.get('primary_game')
        is_verified = request.query_params.get('is_verified')
        
        if search:
            clans = clans.filter(
                Q(name__icontains=search) | 
                Q(tag__icontains=search) | 
                Q(description__icontains=search)
            )
        if country:
            clans = clans.filter(country=country)
        if primary_game:
            clans = clans.filter(primary_game=primary_game)
        if is_verified is not None:
            clans = clans.filter(is_verified=is_verified.lower() == 'true')
        
        serializer = ClanSerializer(clans, many=True)
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': clans.count()
            }
        })
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        data = request.data.copy()
        data['created_by'] = request.user.id
        
        serializer = ClanSerializer(data=data)
        if serializer.is_valid():
            clan = serializer.save()
            # Add creator as leader
            ClanMember.objects.create(
                clan=clan,
                user=request.user,
                role='leader'
            )
            return Response({
                'success': True,
                'data': ClanSerializer(clan).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ClanDetailAPIView(APIView):
    """
    Retrieve, update or delete a clan.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            serializer = ClanSerializer(clan)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if user is a leader or admin of the clan
            try:
                member = ClanMember.objects.get(clan=clan, user=request.user)
                if member.role not in ['leader', 'admin']:
                    return Response(
                        {'error': 'Permission denied'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = ClanSerializer(clan, data=request.data, partial=True)
            if serializer.is_valid():
                clan = serializer.save()
                return Response({
                    'success': True,
                    'data': ClanSerializer(clan).data
                })
            else:
                return Response(
                    {'error': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if user is the leader of the clan
            try:
                member = ClanMember.objects.get(clan=clan, user=request.user)
                if member.role != 'leader':
                    return Response(
                        {'error': 'Only the leader can delete the clan'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            clan.is_active = False
            clan.save()
            return Response({'success': True})
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class JoinClanAPIView(APIView):
    """
    Request to join a clan.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if user is already a member
            if ClanMember.objects.filter(clan=clan, user=request.user).exists():
                return Response(
                    {'error': 'You are already a member of this clan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if there's already a pending request
            if ClanJoinRequest.objects.filter(clan=clan, user=request.user, status='pending').exists():
                return Response(
                    {'error': 'You already have a pending request to join this clan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create join request
            message = request.data.get('message', '')
            join_request = ClanJoinRequest.objects.create(
                clan=clan,
                user=request.user,
                message=message
            )
            
            return Response({
                'success': True,
                'data': ClanJoinRequestSerializer(join_request).data
            })
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class LeaveClanAPIView(APIView):
    """
    Leave a clan.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            try:
                member = ClanMember.objects.get(clan=clan, user=request.user)
                if member.role == 'leader':
                    return Response(
                        {'error': 'Leaders cannot leave the clan. Transfer leadership first or delete the clan.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                member.delete()
                return Response({'success': True})
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ClanMembersAPIView(APIView):
    """
    Get clan members.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            members = ClanMember.objects.filter(clan=clan, is_active=True)
            serializer = ClanMemberSerializer(members, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateMemberRoleAPIView(APIView):
    """
    Update a member's role in the clan.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk, user_id):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if requesting user is leader or admin
            try:
                requesting_member = ClanMember.objects.get(clan=clan, user=request.user)
                if requesting_member.role not in ['leader', 'admin']:
                    return Response(
                        {'error': 'Permission denied'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update member role
            try:
                member = ClanMember.objects.get(clan=clan, user_id=user_id)
                new_role = request.data.get('role')
                if new_role not in ['leader', 'admin', 'captain', 'member', 'recruit']:
                    return Response(
                        {'error': 'Invalid role'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                member.role = new_role
                member.save()
                
                return Response({
                    'success': True,
                    'data': ClanMemberSerializer(member).data
                })
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'Member not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class RemoveMemberAPIView(APIView):
    """
    Remove a member from the clan.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk, user_id):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if requesting user is leader or admin
            try:
                requesting_member = ClanMember.objects.get(clan=clan, user=request.user)
                if requesting_member.role not in ['leader', 'admin']:
                    return Response(
                        {'error': 'Permission denied'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Remove member
            try:
                member = ClanMember.objects.get(clan=clan, user_id=user_id)
                if member.role == 'leader':
                    return Response(
                        {'error': 'Cannot remove the leader'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                member.delete()
                return Response({'success': True})
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'Member not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ClanJoinRequestsAPIView(APIView):
    """
    Get pending join requests for a clan.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if user is leader or admin
            try:
                member = ClanMember.objects.get(clan=clan, user=request.user)
                if member.role not in ['leader', 'admin']:
                    return Response(
                        {'error': 'Permission denied'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            requests = ClanJoinRequest.objects.filter(clan=clan, status='pending')
            serializer = ClanJoinRequestSerializer(requests, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ApproveJoinRequestAPIView(APIView):
    """
    Approve a join request.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, request_id):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if user is leader or admin
            try:
                member = ClanMember.objects.get(clan=clan, user=request.user)
                if member.role not in ['leader', 'admin']:
                    return Response(
                        {'error': 'Permission denied'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Approve join request
            try:
                join_request = ClanJoinRequest.objects.get(
                    id=request_id, 
                    clan=clan, 
                    status='pending'
                )
                
                # Create clan member
                ClanMember.objects.create(
                    clan=clan,
                    user=join_request.user,
                    role='member'
                )
                
                # Update join request status
                join_request.status = 'approved'
                join_request.save()
                
                return Response({'success': True})
            except ClanJoinRequest.DoesNotExist:
                return Response(
                    {'error': 'Join request not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class RejectJoinRequestAPIView(APIView):
    """
    Reject a join request.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, request_id):
        try:
            clan = Clan.objects.get(id=pk, is_active=True)
            
            # Check if user is leader or admin
            try:
                member = ClanMember.objects.get(clan=clan, user=request.user)
                if member.role not in ['leader', 'admin']:
                    return Response(
                        {'error': 'Permission denied'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ClanMember.DoesNotExist:
                return Response(
                    {'error': 'You are not a member of this clan'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Reject join request
            try:
                join_request = ClanJoinRequest.objects.get(
                    id=request_id, 
                    clan=clan, 
                    status='pending'
                )
                
                join_request.status = 'rejected'
                join_request.save()
                
                return Response({'success': True})
            except ClanJoinRequest.DoesNotExist:
                return Response(
                    {'error': 'Join request not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Clan.DoesNotExist:
            return Response(
                {'error': 'Clan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
