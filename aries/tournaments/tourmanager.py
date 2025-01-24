import random
from typing import List,Dict
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import PlayerStats,ClanStats,Clans,Profile
class TourManager:
    def __init__(self, json_data, teams_names, tournament_type,teams_advance=None):
        """
        Initialize the TourManager.

        Args:
            json_data (dict): Data storage for matches.
            teams_names (list): List of team names.
            tournament_type (str): Type of tournament ('league', 'cup', 'league_knockout', 'groups_knockout').
        """
        self.match_data = json_data
        self.teams = teams_names
        self.tournament_type = tournament_type
        self.teams_to_advance = teams_advance
# ============================================================================ #
#                                    leagues                                   #
# ============================================================================ #

    

    def update_elo_for_match(self,winner_name, loser_name, k=32):
        """
        Update Elo ratings for a match.

        Args:
            winner_name (str): Name of the winner (player or clan).
            loser_name (str): Name of the loser (player or clan).
            PlayerStatsModel: Django model for player stats.
            ClanStatsModel: Django model for clan stats.
            k (int): The K-factor for Elo calculation (default: 32).

        Returns:
            None: Updates the database directly.
        """
        def get_player_elo_and_instance(name):
            """Fetch Elo rating and instance from a given player model."""
            #player = User.objects.get(username=name)
            player = User.objects.filter(username__iexact=name).first()
            if player:
                instance = player.profile.stats
                return instance.elo_rating, instance
            else:
                return None, None

        def get_clan_elo_and_instance(name):
            """Fetch Elo rating and instance from the Clans model."""
            clan = get_object_or_404(Clans, clan_name=name)
            try:
                instance = clan.stat 
                return instance.elo_rating, instance
            except clan.DoesNotExist:
                return None, None
        winner_elo, winner_instance = get_player_elo_and_instance(winner_name)
        loser_elo, loser_instance = get_player_elo_and_instance(loser_name)
        stats_used = "player_stats"


        if winner_elo is None or loser_elo is None:
            winner_elo, winner_instance = get_clan_elo_and_instance(winner_name)
            loser_elo, loser_instance = get_clan_elo_and_instance(loser_name)
            stats_used = "clan_stats"

        

        winner_new_elo, loser_new_elo = self.update_elo(winner_elo, loser_elo, k)
        if winner_instance:
            winner_instance.elo_rating = winner_new_elo
            winner_instance.save()
            if stats_used == "player_stats":
                winner_instance.set_rank_based_on_elo()
            else:
                winner_instance.set_rank_based_on_elo()

        if loser_instance:
            loser_instance.elo_rating = loser_new_elo
            loser_instance.save()
            if stats_used == "player_stats":
                loser_instance.set_rank_based_on_elo()
            else:
                loser_instance.set_rank_based_on_elo()
        

    def update_elo(self,winner_elo, loser_elo, k):
        """Calculate Elo rating adjustments."""
        expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
        winner_new_elo = winner_elo + k * (1 - expected_winner)
        loser_new_elo = loser_elo - k * (1 - expected_winner)
        return winner_new_elo, loser_new_elo

    def make_league(self):
        """Creates a round-robin structure for leagues."""
        if len(self.teams) % 2 == 1:
            self.teams.append("Bye")  
        n = len(self.teams)
        round_robin = {
                "fixtures": {},  
                "table": {}
        }
        for round_number in range(n - 1):
            round_matches = []
            for i in range(n // 2):
                home = self.teams[i]
                away = self.teams[n - 1 - i]
                if home == "Bye" or away == "Bye":
                    continue
                round_matches.append({
                    "match":i+1,
                    "team_a": home,
                    "team_b": away,
                    "team_a_goals": None,
                    "team_b_goals": None,
                    "winner": None,
                    "status":'pending'
                })
            round_robin['fixtures'][f"round_{round_number + 1}"] = round_matches
            self.teams.insert(1, self.teams.pop())
        for team in self.teams:
            if team == "Bye":
                continue  # Exclude "Bye" from the table
            round_robin["table"][team] = {
                "goals_scored": 0,
                "goals_conceded": 0,
                "goal_difference": 0,
                "points": 0,
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0
            }
        return round_robin

    def update_league(self,round_number,match_results):
        round_key = f"round_{round_number}"
        if round_key not in self.match_data['fixtures']:
            return
        round_matches = self.match_data['fixtures'][round_key]
        for result in match_results:
            team_a = result["team_a"]
            team_b = result["team_b"]
            match = next((m for m in round_matches if m["team_a"] == team_a and m["team_b"] == team_b), None)
            if match['status'] !="complete":
                if match:
                    match["team_a_goals"] = result["team_a_goals"]
                    match["team_b_goals"] = result["team_b_goals"]

                    team_a = match["team_a"]
                    team_b = match["team_b"]
                    goals_a = result["team_a_goals"]
                    goals_b = result["team_b_goals"]

                    # Determine winner or draw
                    if goals_a > goals_b:
                        match["winner"] = team_a
                        self.update_elo_for_match(team_a,team_b)
                        self.update_table(team_a, goals_a, goals_b, result_type="win")
                        self.update_table(team_b, goals_b, goals_a, result_type="loss")
                    elif goals_a < goals_b:
                        match["winner"] = team_b
                        self.update_elo_for_match(team_b,team_a)
                        self.update_table(team_b, goals_b, goals_a, result_type="win")
                        self.update_table(team_a, goals_a, goals_b, result_type="loss")
                    else:
                        match["winner"] = "Draw"
                        self.update_table(team_a, goals_a, goals_b, result_type="draw")
                        self.update_table(team_b, goals_b, goals_a, result_type="draw")
                    match['status'] ="complete"
        return self.match_data['fixtures'][round_key]
    
    def update_table(self, team, goals_scored, goals_conceded, result_type):
        """Update the league table for a team based on match result."""
        table = self.match_data["table"]
        table[team]["goals_scored"] += goals_scored
        table[team]["goals_conceded"] += goals_conceded
        table[team]["goal_difference"] = (table[team]["goals_scored"] - table[team]["goals_conceded"])
        table[team]["matches_played"] += 1

        if result_type == "win":
            table[team]["wins"] += 1
            table[team]["points"] += 3
        elif result_type == "draw":
            table[team]["draws"] += 1
            table[team]["points"] += 1
        elif result_type == "loss":
            table[team]["losses"] += 1
        sorted_table = sorted(
        table.items(),
        key=lambda item: (
            item[1]["points"], 
            item[1]["goal_difference"], 
            item[1]["wins"], 
            item[1]["goals_scored"]
        ), 
        reverse=True  # Sort in descending order
    )
    
    # Update the table with sorted teams
        self.match_data["table"] = {team[0]: team[1] for team in sorted_table}
        
# ============================================================================ #
#                                   knockouts                                  #
# ============================================================================ #
    def make_knockout(self,teams=None):
        """Creates a knockout structure for cups with bracket-style details."""       
        if not hasattr(self, 'match_data'):
            self.match_data = {}

        if teams is None or 'rounds' not in self.match_data:
            teams = self.teams if teams is None else teams
            self.match_data["rounds"] = []
            self.match_data["table"] = {team: {
                "goals_scored": 0,
                "goals_conceded": 0,
                "goal_difference": 0,
                "points": 0,
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0
            } for team in self.teams}
            round_number = 1
        else:
            round_number = len(self.match_data["rounds"]) + 1

        print(self.match_data)
        random.shuffle(teams)
        while len(teams) > 1:
            round_matches = []
            while len(teams) >= 2:
                team_a = teams.pop(0)
                team_b = teams.pop(0)
                match = {
                    "team_a": team_a,
                    "team_b": team_b,
                    "team_a_goals": None,
                    "team_b_goals": None,
                    "winner": None,
                    "status":"pending"
                }
                round_matches.append(match)
            
            self.match_data["rounds"].append({
                "round_number": round_number,
                "matches": round_matches
            })
            round_number += 1
        
        
        return self.match_data

    def update_knockout(self, round_number, match_results):
        """Updates knockout matches with results and progresses to the next round."""
        rounds = self.match_data.get("rounds", [])
        current_round = next(
            (r for r in rounds if r["round_number"] == round_number), None
        )
        print(current_round)
        if not current_round:
            raise ValueError(f"Round {round_number} not found in knockout data.")
        
        next_round_players = []
        for result in match_results:
            print("Match Results:", result)
            team_a = result["team_a"]
            team_b = result["team_b"]
            
            # Find the match using team names
            match = next(
                (m for m in current_round['matches'] if (m["team_a"] == team_a and m["team_b"] == team_b) or (m["team_a"] == team_b and m["team_b"] == team_a)),
                None
            )
            if match['status'] !="complete":
                match["team_a_goals"] = result["team_a_goals"]
                match["team_b_goals"] = result["team_b_goals"]
                if match["team_a_goals"] > match["team_b_goals"]:
                    match["winner"] = match["team_a"]
                    self.update_elo_for_match(match["team_a"],match["team_b"])
                elif match["team_a_goals"] < match["team_b_goals"]:
                    match["winner"] = match["team_b"]
                    self.update_elo_for_match(match["team_b"],match["team_a"])
                else:
                    match["winner"] = None
                for team, scored, conceded in [
                    (team_a, match["team_a_goals"], match["team_b_goals"]),
                    (team_b, match["team_b_goals"], match["team_a_goals"]),
                ]:
                    if team not in self.match_data["table"]:
                        self.match_data["table"][team] = {
                            "goals_scored": 0,
                            "goals_conceded": 0,
                            "goal_difference": 0,
                            "points": 0,
                            "matches_played": 0,
                            "wins": 0,
                            "draws": 0,
                            "losses": 0,
                        }
                    self.match_data["table"][team]["goals_scored"] += scored
                    self.match_data["table"][team]["goals_conceded"] += conceded
                    self.match_data["table"][team]["goal_difference"] = (
                        self.match_data["table"][team]["goals_scored"] -
                        self.match_data["table"][team]["goals_conceded"]
                    )
                    self.match_data["table"][team]["matches_played"] += 1

                    if match["winner"] == team:
                        self.match_data["table"][team]["wins"] += 1
                        self.match_data["table"][team]["points"] += 3
                    elif match["winner"] is None:
                        self.match_data["table"][team]["draws"] += 1
                        self.match_data["table"][team]["points"] += 1
                    else:
                        self.match_data["table"][team]["losses"] += 1

                match['status'] = 'complete'
            # Check if all matches are complete
            all_matches_complete = all(match.get('status') == 'complete' for match in current_round['matches'])

            if all_matches_complete:
                for match in current_round['matches']:
                    next_team = match["winner"]
                    next_round_players.append(next_team)
                if next_round_players:
                    print(next_round_players)
                    self.make_knockout(next_round_players)
                    print('here')
            else:
                print("Not all matches are complete yet.")

                    
        return self.match_data

#                                cup with groups                               #
# ============================================================================ #
    def make_groups_knockout(self) -> Dict:
        """Creates a groups + knockout structure."""
        if len(self.teams) !=0:
            min_group_size = 4

        # Calculate the number of groups. Each group should have at least 3 teams.
            groups_count = len(self.teams) // min_group_size
            if len(self.teams) % min_group_size != 0:
                groups_count += 1 
            groups = {}
            group_matches = {}  # Initialize group matches
            random.shuffle(self.teams)
            group_size = len(self.teams) // groups_count
            remainder = len(self.teams) % groups_count

            # Distribute teams into groups
            start_index = 0
            for i in range(groups_count):
                group_name = f"Group {chr(65 + i)}"  # Example: "Group A", "Group B"
                end_index = start_index + group_size + (1 if remainder > 0 else 0)
                groups[group_name] = self.teams[start_index:end_index]
                start_index = end_index
                if remainder > 0:
                    remainder -= 1

            # Create group matches
            for group_name, group_teams in groups.items():
                group_manager = TourManager(self.match_data, group_teams, "league")
                group_matches[group_name] = group_manager.make_league()

            self.match_data = {"group_stages":group_matches}
            return  self.match_data
     
    
    def update_groups_knockout(self, round_number, match_results) -> None:
        """
        Updates match results for a specific round and group in the groups + knockout stage.

        Args:
            round_number (int): The round number to update.
            group (str): The group identifier (e.g., "Group A").
            match_results (List[Dict[str, Union[int, str]]]): List of match results. Each result must contain:
                - "match" (int): Match number.
                - "team_a_goals" (int): Goals scored by Team A.
                - "team_b_goals" (int): Goals scored by Team B.
        Returns:
            None
        """

        next_round_players = []        
        for group_name,group_data in self.match_data["group_stages"].items():
            round_key = f"round_{round_number}"
            group_matches = group_data['fixtures']      
            for result in match_results:
                team_a = result["team_a"]
                team_b = result["team_b"]
                team_a_goals = result.get("team_a_goals")
                team_b_goals = result.get("team_b_goals")
                match = next((m for m in group_matches[round_key] if (m["team_a"] == team_a and m["team_b"] == team_b) or (m["team_a"] == team_b and m["team_b"] == team_a)), None)
                if match:
                    if match['status'] != "complete":
                        match["team_a_goals"] = team_a_goals
                        match["team_b_goals"] = team_b_goals
                        match["status"] = "complete"
                        if team_a_goals > team_b_goals:
                            match["winner"] = match["team_a"]
                            self.update_elo_for_match(match["team_a"], match["team_b"])
                            self.update_group_table(team_a, team_a_goals, team_b_goals, "win", group_data)
                            self.update_group_table(team_b, team_b_goals, team_a_goals, "loss", group_data)
                        elif team_a_goals < team_b_goals:
                            match["winner"] = match["team_b"]
                            self.update_elo_for_match(match["team_b"], match["team_a"])
                            self.update_group_table(team_a, team_a_goals, team_b_goals, "loss", group_data)
                            self.update_group_table(team_b, team_b_goals, team_a_goals, "win", group_data)
                        else:
                            match["winner"] = "Draw"
                            self.update_group_table(team_a, team_a_goals, team_b_goals, "draw", group_data)
                            self.update_group_table(team_b, team_b_goals, team_a_goals, "draw", group_data)
    
            all_matches_complete = all(match.get('status') == 'complete' for round_matches in group_matches.values() for match in round_matches)
            if all_matches_complete:
                teams_to_advance = self.teams_to_advance if self.teams_to_advance else 2
                print(teams_to_advance)
                rankings = list(group_data["table"].keys())
                next_round_players = rankings[:teams_to_advance]
                print(next_round_players)
                self.make_group_knockout(self.match_data,next_round_players)
                print(group_data['table'])
            else:
                print("not done")
    
        return self.match_data
    
    def update_group_table(self, team, goals_scored, goals_conceded, result_type,group_data):
        """Update the league table for a team based on match result."""
        table = group_data["table"]
        table[team]["goals_scored"] += goals_scored
        table[team]["goals_conceded"] += goals_conceded
        table[team]["goal_difference"] = (table[team]["goals_scored"] - table[team]["goals_conceded"])
        table[team]["matches_played"] += 1
        if result_type == "win":
            table[team]["wins"] += 1
            table[team]["points"] += 3
        elif result_type == "draw":
            table[team]["draws"] += 1
            table[team]["points"] += 1
        elif result_type == "loss":
            table[team]["losses"] += 1
        sorted_table = sorted(
        table.items(),
        key=lambda item: (
            item[1]["points"], 
            item[1]["goal_difference"], 
            item[1]["wins"], 
            item[1]["goals_scored"]
        ), 
        reverse=True )
        group_data["table"] = {team[0]: team[1] for team in sorted_table}

    def make_group_knockout(self, data, teams):
        """Creates a knockout structure for cups with bracket-style details."""       
        if 'knock_outs' not in data:
            data["knock_outs"] = {"rounds":[],"table": {}}
            data["knock_outs"]["table"] = {team: {
                "goals_scored": 0,
                "goals_conceded": 0,
                "goal_difference": 0,
                "points": 0,
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0
            } for team in teams}
            round_number = 1
        else:
            round_number = len(data["rounds"]) + 1
        random.shuffle(teams)

        while len(teams) > 1:
            round_matches = []
            while len(teams) >= 2:
                team_a = teams.pop(0)
                team_b = teams.pop(0)
                match = {
                    "team_a": team_a,
                    "team_b": team_b,
                    "team_a_goals": None,
                    "team_b_goals": None,
                    "winner": None,
                    "status": "pending"
                }
                round_matches.append(match)
            
            # Append the round with its matches
            data["knock_outs"]["rounds"].append({
                "round_number": round_number,
                "matches": round_matches
            })
            round_number += 1

   
        return data
                
    def update_ko(self, round_number, match_results):
        """Updates knockout matches with results and progresses to the next round."""
        rounds = self.match_data["knock_outs"].get("rounds", [])
        current_round = next(
            (r for r in rounds if r["round_number"] == round_number), None
        )
        print(current_round)
        if not current_round:
            raise ValueError(f"Round {round_number} not found in knockout data.")
        
        next_round_players = []
        for result in match_results:
            print("Match Results:", result)
            team_a = result["team_a"]
            team_b = result["team_b"]
            
            # Find the match using team names
            match = next(
                (m for m in current_round['matches'] if (m["team_a"] == team_a and m["team_b"] == team_b) or (m["team_a"] == team_b and m["team_b"] == team_a)),
                None
            )
            if match['status'] !="complete":
                match["team_a_goals"] = result["team_a_goals"]
                match["team_b_goals"] = result["team_b_goals"]
                if match["team_a_goals"] > match["team_b_goals"]:
                    match["winner"] = match["team_a"]
                    self.update_elo_for_match(match["team_a"],match["team_b"])
                elif match["team_a_goals"] < match["team_b_goals"]:
                    match["winner"] = match["team_b"]
                    self.update_elo_for_match(match["team_b"],match["team_a"])
                else:
                    match["winner"] = None
                for team, scored, conceded in [
                    (team_a, match["team_a_goals"], match["team_b_goals"]),
                    (team_b, match["team_b_goals"], match["team_a_goals"]),
                ]:
                    if team not in self.match_data["knock_outs"]["table"]:
                        self.match_data["knock_outs"]["table"][team] = {
                            "goals_scored": 0,
                            "goals_conceded": 0,
                            "goal_difference": 0,
                            "points": 0,
                            "matches_played": 0,
                            "wins": 0,
                            "draws": 0,
                            "losses": 0,
                        }
                    self.match_data["knock_outs"]["table"][team]["goals_scored"] += scored
                    self.match_data["knock_outs"]["table"][team]["goals_conceded"] += conceded
                    self.match_data["knock_outs"]["table"][team]["goal_difference"] = (
                        self.match_data["knock_outs"]["table"][team]["goals_scored"] -
                        self.match_data["knock_outs"]["table"][team]["goals_conceded"]
                    )
                    self.match_data["knock_outs"]["table"][team]["matches_played"] += 1

                    if match["winner"] == team:
                        self.match_data["knock_outs"]["table"][team]["wins"] += 1
                        self.match_data["knock_outs"]["table"][team]["points"] += 3
                    elif match["winner"] is None:
                        self.match_data["knock_outs"]["table"][team]["draws"] += 1
                        self.match_data["knock_outs"]["table"][team]["points"] += 1
                    else:
                        self.match_data["knock_outs"]["table"][team]["losses"] += 1

                match['status'] = 'complete'
            # Check if all matches are complete
            all_matches_complete = all(match.get('status') == 'complete' for match in current_round['matches'])

            if all_matches_complete:
                for match in current_round['matches']:
                    next_team = match["winner"]
                    next_round_players.append(next_team)
                if len(next_round_players) > 1:
                    print(next_round_players)
                    self.make_group_knockout(self.match_data,next_round_players)
                    print('here')
            else:
                print("Not all matches are complete yet.")

                    
        return self.match_data


    def create_tournament(self):
        """Creates the specified tournament type."""
        if self.tournament_type == "league":
            return self.make_league()
        elif self.tournament_type == "cup":
            return self.make_knockout()
        elif self.tournament_type == "groups_knockout":
            return self.make_groups_knockout()
        else:
            raise ValueError(f"Unknown tournament type: {self.tournament_type}")
       