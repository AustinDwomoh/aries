from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from clans.models import Clan
from users.models import Profile
from scripts.error_handle import ErrorHandler
from scripts.follow import get_followed_instance, get_followers, get_following
from users.serializers import UserSerializer, ProfileSerializer
from clans.serializers import ClanSerializer


class HomeStatsAPIView(APIView):
    """
    API endpoint to get home page statistics (top players and clans).
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # Get top clans by ELO rating
            clans = Clan.objects.select_related('stats').filter(
                is_verified=True
            ).order_by('-stats__elo_rating')[:10]
            
            # Get top players by ELO rating
            players = User.objects.select_related('profile__stats').filter(
                profile__stats__isnull=False
            ).order_by('-profile__stats__elo_rating')[:10]
            
            # Serialize the data
            clans_data = ClanSerializer(clans, many=True).data
            players_data = []
            
            for player in players:
                player_data = UserSerializer(player).data
                if hasattr(player, 'profile') and player.profile:
                    player_data['profile'] = ProfileSerializer(player.profile).data
                players_data.append(player_data)
            
            return Response({
                'success': True,
                'data': {
                    'top_clans': clans_data,
                    'top_players': players_data
                }
            })
            
        except Exception as e:
            ErrorHandler().handle(e, context="Home Stats API")
            return Response(
                {'error': 'Failed to fetch home statistics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FollowListAPIView(APIView):
    """
    API endpoint to get followers or following lists for a profile.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, model, profile_id, ftype):
        if ftype not in ['followers', 'following']:
            return Response(
                {'error': 'Invalid follow type. Must be "followers" or "following".'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            instance = get_followed_instance(model, profile_id)
            if not instance:
                return Response(
                    {'error': 'Profile not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if ftype == 'followers':
                data = get_followers(instance)
            else:
                data = get_following(instance)
            
            # Serialize the data
            users_data = []
            clans_data = []
            
            for user in data.get("users", []):
                user_data = UserSerializer(user).data
                if hasattr(user, 'profile') and user.profile:
                    user_data['profile'] = ProfileSerializer(user.profile).data
                users_data.append(user_data)
            
            for clan in data.get("clans", []):
                clans_data.append(ClanSerializer(clan).data)
            
            return Response({
                'success': True,
                'data': {
                    'users': users_data,
                    'clans': clans_data,
                    'view_type': ftype,
                    'profile_id': profile_id
                }
            })
            
        except Exception as e:
            ErrorHandler().handle(e, context=f"Follow List API - {ftype}")
            return Response(
                {'error': 'Failed to fetch follow list'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdsTxtAPIView(APIView):
    """
    API endpoint for ads.txt file.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response(
            "google.com, pub-6095628428301944, DIRECT, f08c47fec0942fa0",
            content_type="text/plain"
        )
