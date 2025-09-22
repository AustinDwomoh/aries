from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Tournament, TournamentParticipant, Match
from .serializers import TournamentSerializer, TournamentParticipantSerializer, MatchSerializer
from organizations.models import Organization
from clans.models import Clan
from django.contrib.auth.models import User


class TournamentListCreateAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        tournaments = Tournament.objects.all().order_by('-created_at')
        
        # Apply filters
        tournament_type = request.query_params.get('tournament_type')
        status_filter = request.query_params.get('status')
        organizer = request.query_params.get('organizer')
        
        if tournament_type:
            tournaments = tournaments.filter(tournament_type=tournament_type)
        if status_filter:
            tournaments = tournaments.filter(status=status_filter)
        if organizer:
            tournaments = tournaments.filter(organizer_id=organizer)
        
        serializer = TournamentSerializer(tournaments, many=True)
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': tournaments.count()
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
        
        # Get organizer
        organizer_id = data.get('organizer')
        if not organizer_id:
            return Response(
                {'error': 'Organizer is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            organizer = Organization.objects.get(id=organizer_id)
            data['organizer'] = organizer.id
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Invalid organizer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TournamentSerializer(data=data)
        if serializer.is_valid():
            tournament = serializer.save()
            return Response({
                'success': True,
                'data': TournamentSerializer(tournament).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class TournamentDetailAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        try:
            tournament = Tournament.objects.get(id=pk)
            serializer = TournamentSerializer(tournament)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Tournament not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            tournament = Tournament.objects.get(id=pk)
            if tournament.created_by != request.user:
                return Response(
                    {'error': 'Permission denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = TournamentSerializer(tournament, data=request.data, partial=True)
            if serializer.is_valid():
                tournament = serializer.save()
                return Response({
                    'success': True,
                    'data': TournamentSerializer(tournament).data
                })
            else:
                return Response(
                    {'error': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Tournament not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            tournament = Tournament.objects.get(id=pk)
            if tournament.created_by != request.user:
                return Response(
                    {'error': 'Permission denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            tournament.delete()
            return Response({'success': True})
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Tournament not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class JoinTournamentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            tournament = Tournament.objects.get(id=pk)
            
            # Check if user is already participating
            existing_participant = TournamentParticipant.objects.filter(
                tournament=tournament,
                user=request.user
            ).first()
            
            if existing_participant:
                return Response(
                    {'error': 'Already participating in this tournament'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create participant
            participant = TournamentParticipant.objects.create(
                tournament=tournament,
                user=request.user
            )
            
            return Response({
                'success': True,
                'data': TournamentParticipantSerializer(participant).data
            })
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Tournament not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class LeaveTournamentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            tournament = Tournament.objects.get(id=pk)
            participant = TournamentParticipant.objects.get(
                tournament=tournament,
                user=request.user
            )
            participant.delete()
            return Response({'success': True})
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Tournament not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except TournamentParticipant.DoesNotExist:
            return Response(
                {'error': 'Not participating in this tournament'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class TournamentMatchesAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        try:
            tournament = Tournament.objects.get(id=pk)
            matches = Match.objects.filter(tournament=tournament).order_by('round_number', 'match_number')
            serializer = MatchSerializer(matches, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Tournament not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateMatchResultAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk, match_id):
        try:
            tournament = Tournament.objects.get(id=pk)
            match = Match.objects.get(id=match_id, tournament=tournament)
            
            # Check if user has permission to update match
            if tournament.created_by != request.user:
                return Response(
                    {'error': 'Permission denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = MatchSerializer(match, data=request.data, partial=True)
            if serializer.is_valid():
                match = serializer.save()
                return Response({
                    'success': True,
                    'data': MatchSerializer(match).data
                })
            else:
                return Response(
                    {'error': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Tournament not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Match.DoesNotExist:
            return Response(
                {'error': 'Match not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
