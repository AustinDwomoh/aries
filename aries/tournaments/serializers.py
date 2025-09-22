from rest_framework import serializers
from .models import Tournament, TournamentParticipant, Match
from organizations.serializers import OrganizationSerializer
from clans.serializers import ClanSerializer
from users.serializers import UserSerializer


class TournamentParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    clan = ClanSerializer(read_only=True)
    
    class Meta:
        model = TournamentParticipant
        fields = ['id', 'tournament', 'user', 'clan', 'joined_at', 'status']
        read_only_fields = ['id', 'joined_at']


class MatchSerializer(serializers.ModelSerializer):
    home_participant = TournamentParticipantSerializer(read_only=True)
    away_participant = TournamentParticipantSerializer(read_only=True)
    winner = TournamentParticipantSerializer(read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'tournament', 'round_number', 'match_number',
            'home_participant', 'away_participant', 'home_score', 'away_score',
            'winner', 'match_date', 'is_completed'
        ]
        read_only_fields = ['id', 'winner']


class TournamentSerializer(serializers.ModelSerializer):
    organizer = OrganizationSerializer(read_only=True)
    participants = TournamentParticipantSerializer(many=True, read_only=True)
    matches = MatchSerializer(many=True, read_only=True)
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'description', 'created_by', 'organizer',
            'tournament_type', 'tour_format', 'status', 'start_date', 'end_date',
            'max_participants', 'entry_fee', 'prize_pool', 'home_or_away',
            'logo', 'match_data', 'participants', 'matches', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'match_data']
