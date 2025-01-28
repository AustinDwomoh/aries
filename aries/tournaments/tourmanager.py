import random
from django.utils import timezone
from typing import List,Dict
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import PlayerStats,ClanStats,Clans,Profile
class TourManager:
    def __init__(self, json_data, teams_names, tournament_type,teams_advance=None,tour_name="Not specifed"):
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
        self.tour_name = tour_name
# ============================================================================ #
#                                    leagues                                   #
# ============================================================================ #

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
                        self.store_records(team_a, team_b, goals_a, goals_b)
                        self.update_team_db_stats(team_a, goals_a, goals_b, result_type="win")
                        self.update_team_db_stats(team_b, goals_b, goals_a, result_type="loss")
                    elif goals_a < goals_b:
                        match["winner"] = team_b
                        self.update_elo_for_match(team_b,team_a)
                        self.update_table(team_b, goals_b, goals_a, result_type="win")
                        self.update_table(team_a, goals_a, goals_b, result_type="loss")
                        self.store_records(team_b, team_a, goals_b, goals_a)
                        self.update_team_db_stats(team_a, goals_a, goals_b, result_type="loss")
                        self.update_team_db_stats(team_b, goals_b, goals_a, result_type="win")
                    else:
                        match["winner"] = "Draw"
                        self.update_table(team_a, goals_a, goals_b, result_type="draw")
                        self.update_table(team_b, goals_b, goals_a, result_type="draw")
                        self.store_records(team_a, team_b, goals_a, goals_b, result_type="draw")
                        self.update_team_db_stats(team_a, goals_a, goals_b)
                        self.update_team_db_stats(team_b, goals_b, goals_a)
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
                    self.store_records(team_a, team_b, match["team_a_goals"], match["team_b_goals"])
                    self.update_team_db_stats(team_a,  match["team_a_goals"], match["team_b_goals"], result_type="win")
                    self.update_team_db_stats(team_b,  match["team_b_goals"], match["team_a_goals"], result_type="loss")
                elif match["team_a_goals"] < match["team_b_goals"]:
                    match["winner"] = match["team_b"]
                    self.update_elo_for_match(match["team_b"],match["team_a"])
                    self.store_records(team_b, team_a, match["team_b_goals"], match["team_a_goals"])
                    self.update_team_db_stats(team_a,  match["team_a_goals"], match["team_b_goals"], result_type="loss")
                    self.update_team_db_stats(team_b,  match["team_b_goals"], match["team_a_goals"], result_type="win")
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
                    self.make_knockout(next_round_players)
                    
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
                            self.store_records(team_a, team_b, team_a_goals, team_b_goals)
                            self.update_team_db_stats(team_a, team_a_goals, team_b_goals, result_type="win")
                            self.update_team_db_stats(team_b, team_b_goals, team_a_goals, result_type="loss")
                        elif team_a_goals < team_b_goals:
                            match["winner"] = match["team_b"]
                            self.update_elo_for_match(match["team_b"], match["team_a"])
                            self.update_group_table(team_a, team_a_goals, team_b_goals, "loss", group_data)
                            self.update_group_table(team_b, team_b_goals, team_a_goals, "win", group_data)
                            self.update_team_db_stats(team_a, team_a_goals, team_b_goals, result_type="loss")
                            self.update_team_db_stats(team_b, team_b_goals, team_a_goals, result_type="win")
                            
                        else:
                            match["winner"] = "Draw"
                            self.update_group_table(team_a, team_a_goals, team_b_goals, "draw", group_data)
                            self.update_group_table(team_b, team_b_goals, team_a_goals, "draw", group_data)
                            self.store_records(team_b, team_a, team_b_goals, team_a_goals,result_type="draw")
                            self.update_team_db_stats(team_a, team_a_goals, team_b_goals)
                            self.update_team_db_stats(team_b, team_b_goals, team_a_goals)
    
            all_matches_complete = all(match.get('status') == 'complete' for round_matches in group_matches.values() for match in round_matches)
            if all_matches_complete:
                teams_to_advance = self.teams_to_advance if self.teams_to_advance else 2
                rankings = list(group_data["table"].keys())
                next_round_players = rankings[:teams_to_advance]
                self.make_group_knockout(self.match_data,next_round_players) 
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
                    self.store_records(team_a, team_b, match["team_a_goals"], match["team_b_goals"])
                    self.update_team_db_stats(team_a,  match["team_a_goals"], match["team_b_goals"], result_type="win")
                    self.update_team_db_stats(team_b,  match["team_b_goals"], match["team_a_goals"], result_type="loss")
                elif match["team_a_goals"] < match["team_b_goals"]:
                    match["winner"] = match["team_b"]
                    self.update_elo_for_match(match["team_b"],match["team_a"])
                    self.store_records(team_b, team_a, match["team_b_goals"], match["team_a_goals"])
                    self.update_team_db_stats(team_a,  match["team_a_goals"], match["team_b_goals"], result_type="loss")
                    self.update_team_db_stats(team_b,  match["team_b_goals"], match["team_a_goals"], result_type="win")
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
                    self.make_group_knockout(self.match_data,next_round_players)
        return self.match_data

# ============================================================================ #
#                                Init for tours                                #
# ============================================================================ #
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
        
# ============================================================================ #
#                       stat update for clans and players                      #
# ============================================================================ #
    def store_records(self, winner, loser, winner_goals, loser_goals, result_type="win"):
        """
        Update and store  records for the match result.

        Args:
            winner (Profile): The profile of the winning team.
            loser (Profile): The profile of the losing team.
            winner_goals (int): Goals scored by the winner.
            loser_goals (int): Goals scored by the loser.
            result_type (str): Type of result ('win', 'draw').
        """
        def get_player_stats(winner, loser):
            """Fetch PlayerStats instances for both winner and loser."""
            try:
                winner = User.objects.filter(username__iexact=winner).first()
                loser = User.objects.filter(username__iexact=loser).first()
                if winner and loser:
                    loser_stats = loser.profile.stats
                    winner_stats = winner.profile.stats 
                    return winner_stats, loser_stats
            except ObjectDoesNotExist:
                return None, None
            return None, None 

        def get_clan_stats(winner, loser):
            """Fetch ClanStats instances for both winner and loser."""
            try:
                winner = get_object_or_404(Clans, clan_name=winner)
                loser = get_object_or_404(Clans, clan_name=loser)
                if winner and loser:
                    loser_stats = loser.stat
                    winner_stats = winner.stat
                return winner_stats, loser_stats
            except ObjectDoesNotExist:
                return None, None
            return None, None 
        winner_stats, loser_stats = get_player_stats(winner, loser)
        stats_used = "player_stats" 

        if winner_stats is None or loser_stats is None:
            winner_stats, loser_stats = get_clan_stats(winner, loser)
            stats_used = "clan_stats"

        winner_data = winner_stats.load_match_data_from_file()
        loser_data = loser_stats.load_match_data_from_file()
        if result_type == "win":
            winner_result = "win"
            loser_result = "loss"
        elif result_type == "draw":
            winner_result = "draw"
            loser_result = "draw"
        winner_entry = {
            "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tour_name":self.tour_name, 
            "opponent": loser,  
            "result": winner_result, 
            "score": f"{winner_goals}:{loser_goals}"
        }
        loser_entry = {
            "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tour_name":self.tour_name,   
            "opponent": winner,  
            "result": loser_result, 
            "score":f"{loser_goals}:{winner_goals}"
        }

        if "matches" not in winner_data:
            winner_data["matches"] = []
        if "matches" not in loser_data:
            loser_data["matches"] = []

        winner_data["matches"].append(winner_entry)
        loser_data["matches"].append(loser_entry)
        winner_stats.match_data = winner_data 
        loser_stats.match_data = loser_data 
        winner_stats.save_match_data_to_file()
        loser_stats.save_match_data_to_file()

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
            
        def update_elo(winner_elo, loser_elo, k):
            """Calculate Elo rating adjustments."""
            expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
            winner_new_elo = winner_elo + k * (1 - expected_winner)
            loser_new_elo = loser_elo - k * (1 - expected_winner)
            return winner_new_elo, loser_new_elo
        winner_elo, winner_instance = get_player_elo_and_instance(winner_name)
        loser_elo, loser_instance = get_player_elo_and_instance(loser_name)
        stats_used = "player_stats"


        if winner_elo is None or loser_elo is None:
            winner_elo, winner_instance = get_clan_elo_and_instance(winner_name)
            loser_elo, loser_instance = get_clan_elo_and_instance(loser_name)
            stats_used = "clan_stats"

        

        winner_new_elo, loser_new_elo = update_elo(winner_elo, loser_elo, k)
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

        

    def update_team_db_stats(self,team,gf,ga,result_type="draw"):
        """
        Update clan statistics based on the tournament results.
        """
        if ClanStats.objects.get(clan__clan_name=team):
            clan_stat = ClanStats.objects.get(clan__clan_name=team)
            clan_stat.gd += gf-ga
            clan_stat.gf += gf
            clan_stat.ga += ga
            clan_stat.total_matches += 1
            if result_type =="win":
                clan_stat.wins += 1
            elif result_type == "loss":
                clan_stat.losses += 1
            else:
                clan_stat.draws += 1
            win_rate = ((clan_stat.wins + clan_stat.draws/2) / clan_stat.total_matches) * 100 if clan_stat.total_matches > 0 else 0
            clan_stat.win_rate = round(win_rate,3)
            clan_stat.save()
        elif User.objects.get(username=team):
            user = User.objects.get(username=team)
            user_stat = user.profile.stats
            user_stat.gd += gf-ga
            user_stat.gf += gf
            user_stat.ga += ga
            user_stat.games_played += 1
            if result_type =="win":
                user_stat.total_wins  += 1
            elif result_type == "loss":
                user_stat.total_losses += 1
            else:
                user_stat.total_draws  += 1
            win_rate = ((user_stat.total_wins + user_stat.total_draws/2) / user_stat.games_played) * 100 if user_stat.games_played > 0 else 0
            user_stat.win_rate = round(win_rate,3)
            user_stat.save()