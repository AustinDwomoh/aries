import random,string,secrets
from django.http import Http404
from django.utils import timezone
from typing import Dict
from scripts.error_handle import ErrorHandler
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from clans.models import Clan

class TourManager:
    """ 
    TourManager class for managing tournament fixtures and results.
    """
    def __init__(self, json_data, teams_names, tournament_type, home_or_away, teams_advance=None, tour_name="Not specified"):
        """
        Initialize the TourManager.

        Args:
            json_data (dict): Storage for match data, a dictionary with match details.
            teams_names (list): List of team names participating in the tournament.
            tournament_type (str): Type of tournament, e.g., 'league', 'cup', 'groups_knockout'.
            home_or_away (str): A flag for determining if matches are home/away.
            teams_advance (int, optional): Number of teams that advance to next round (if applicable).
            tour_name (str, optional): Name of the tournament or tour. Defaults to "Not specified".
        """
        self.match_data = json_data
        self.teams = teams_names
        self.tournament_type = tournament_type
        self.teams_to_advance = teams_advance
        self.tour_name = tour_name
        self.home_or_away= home_or_away
    # ============================================================================ #
    #                                    leagues                                   #
    # ============================================================================ #

    def make_league(self):
        """ 
        Generates a round-robin schedule for a league tournament. It creates fixtures where each team plays every other team once (or twice if home and away is enabled), handles odd numbers of teams by adding a bye, and initializes a standings table for tracking results. Returns a dictionary containing all rounds’ fixtures and the empty league table.
        """
        round_robin = {}
        try:
            teams = self.teams[:]
            if not teams or len(teams) < 2:
                raise ValueError("At least 2 teams required.")

            if len(set(teams)) != len(teams):
                raise ValueError("Duplicate team names found.")

            if len(teams) % 2 == 1:
                teams.append("Bye")  
            n = len(teams)
            match_id = 1
            round_robin = {
                    "fixtures": {},  
                    "table": {}
            }
            for round_number in range(n - 1):
                round_matches = []
                for i in range(n // 2):
                    home = teams[i]
                    away = teams[n - 1 - i]
                    if home == "Bye" or away == "Bye":
                        continue
                    round_matches.append({
                        "match":match_id,
                        "team_a": home,
                        "team_b": away,
                        "team_a_goals": None,
                        "team_b_goals": None,
                        "winner": None,
                        "status":'pending'
                    })
                    match_id += 1
                round_robin['fixtures'][f"round_{round_number + 1}"] = round_matches
                teams.insert(1, teams.pop())
            if self.home_or_away:
                original_rounds = list(round_robin["fixtures"].items())
                for round_number, matches in original_rounds:
                    new_round_matches = []
                    for match in matches:
                        new_round_matches.append({
                            "match": match_id,
                            "team_a": match["team_b"],     # swap
                            "team_b": match["team_a"],     # swap
                            "team_a_goals": None,
                            "team_b_goals": None,
                            "winner": None,
                            "status": 'pending'
                        })
                        match_id += 1
                    new_round_key = f"round_{len(round_robin['fixtures']) + 1}"
                    round_robin['fixtures'][new_round_key] = new_round_matches
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
            
        except Exception as e:
            ErrorHandler().handle(e,context='Failed to make league')
        finally:
           return round_robin 

    def update_league(self,round_number,match_results):
        """
        Updates the league fixtures and table based on match results for a specific round.

        Args:
            round_number (int): The round number to update (1-based index).
            match_results (List[Dict]): List of result dictionaries, each containing:
                - "team_a" (str): Name of team A.
                - "team_b" (str): Name of team B.
                - "team_a_goals" (int): Goals scored by team A.
                - "team_b_goals" (int): Goals scored by team B.

        Returns:
            dict: Updated match_data with fixtures and table info.
        """
        try:
            round_key = f"round_{round_number}"
            if round_key not in self.match_data['fixtures']:
                return
            round_matches = self.match_data['fixtures'][round_key]
            for result in match_results:
                team_a = result["team_a"]
                team_b = result["team_b"]
                goals_a = result["team_a_goals"]
                goals_b = result["team_b_goals"]
                match = next((m for m in round_matches if m["team_a"] == team_a and m["team_b"] == team_b), None)
                if match and match['status'] !="complete":
                    self.finalize_match_result(team_a,team_b,goals_a,goals_b,match)
            
        except Exception as e:
            ErrorHandler().handle(e,context=f"Failed to update league round {round_number} in {self.tour_name}")
        finally:
            return self.match_data
  
    # ============================================================================ #
    #                                   knockouts                                  #
    # ============================================================================ #
    
    def make_knockout(self, teams=None) -> Dict:
        """
        Creates a knockout structure for tournaments with optional home/away legs.
        Can be used for full knockout brackets or knockout after group stages.

        Args:
            teams (list): List of team names. If None, uses self.teams.
            target (str): Target key in self.match_data (e.g. "knock_outs" or "rounds").

        Returns:
            dict: Knockout match structure.
        """
        try:
            target="knock_outs"
            if not hasattr(self, 'match_data'):
                self.match_data = {}

            teams = list(teams or self.teams)
            random.shuffle(teams)

            if target not in self.match_data:
                self.match_data[target] = {"rounds": [], "table": {}}

            self.match_data[target]["table"] = {
                team: {
                    "goals_scored": 0,
                    "goals_conceded": 0,
                    "goal_difference": 0,
                    "points": 0,
                    "matches_played": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0
                } for team in teams
            }

            round_number = 1
            current_participants = [{"name": team} for team in teams]

            while len(current_participants) > 1:
                random.shuffle(current_participants)
                round_matches = []
                next_round_participants = []

                while len(current_participants) >= 2:
                    team_a = current_participants.pop(0)
                    team_b = current_participants.pop(0)

                    match_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

                    if getattr(self, "home_or_away", False):
                        match = {
                            "match_id": match_id,
                            "legs": [
                                {
                                    "leg_number": 1,
                                    "team_a": team_a,
                                    "team_b": team_b,
                                    "team_a_goals": None,
                                    "team_b_goals": None,
                                    "status": "pending"
                                },
                                {
                                    "leg_number": 2,
                                    "team_a": team_b,
                                    "team_b": team_a,
                                    "team_a_goals": None,
                                    "team_b_goals": None,
                                    "status": "pending"
                                }
                            ],
                            "aggregate_team_a_goals": 0,
                            "aggregate_team_b_goals": 0,
                            "winner": None,
                            "status": "pending"
                        }
                    else:
                        match = {
                            "match_id": match_id,
                            "team_a": team_a,
                            "team_b": team_b,
                            "team_a_goals": None,
                            "team_b_goals": None,
                            "winner": None,
                            "status": "pending"
                        }

                    round_matches.append(match)
                    next_round_participants.append({"source_match": match_id, "name": None})

                
                if current_participants:
                    next_round_participants.append(current_participants.pop(0))

                self.match_data[target]["rounds"].append({
                    "round_number": round_number,
                    "matches": round_matches
                })

                current_participants = next_round_participants
                round_number += 1

            
        except Exception as e:
            ErrorHandler().handle(e,context='Failed to make knockouts')
        finally:
            return self.match_data[target]
        
    def update_knockout(self, round_number: int, match_results: list[dict]) -> dict:
        """
        Updates results for a knockout round and progresses the tournament to the next round if all matches are complete.

        Args:
            round_number (int): The current knockout round number (1-based index).
            match_results (List[Dict]): List of match results. Each result should include:
                - "team_a" (str): Name of team A.
                - "team_b" (str): Name of team B.
                - "team_a_goals" (int): Goals scored by team A.
                - "team_b_goals" (int): Goals scored by team B.

        Raises:
            ValueError: If the specified round is not found in knockout data.

        Returns:
            dict: The updated match_data including knockout progress.
        """
        try:
            rounds = self.match_data.get("rounds", [])
            current_round = next((r for r in rounds if r["round_number"] == round_number), None)
            if not current_round:
                raise ValueError(f"Round {round_number} not found in knockout data.")
            
            for result in match_results:
                team_a = result["team_a"]
                team_b = result["team_b"]
                goals_a = result["team_a_goals"]
                goals_b = result["team_b_goals"]
                leg_number = result.get("leg_number")
                match = None
                for m in current_round["matches"]:
                    if "legs" in m:
                        for leg in m["legs"]:
                            name_a = leg.get("team_a", {}).get("name")
                            name_b = leg.get("team_b", {}).get("name")
                            if ((name_a == team_a and name_b == team_b) or
                                (name_a == team_b and name_b == team_a)) and leg["leg_number"] == leg_number:
                                match = m
                                
                                break
                        if match:
                            break
                    else:
                        name_a = m.get("team_a", {}).get("name")
                        name_b = m.get("team_b", {}).get("name")
                        if ((name_a == team_a and name_b == team_b) or
                            (name_a == team_b and name_b == team_a)):
                            match = m
                            break

                if not match:
                    continue
                    
                if "legs" in match:
                    leg = next((l for l in match["legs"] if l["leg_number"] == leg_number),None)
                    if leg and leg["status"] != "complete":
                        leg["team_a_goals"] = goals_a
                        leg["team_b_goals"] = goals_b
                        leg["status"] = "complete"

                    if all(l["status"] == "complete" for l in match["legs"]):
                        total_a = sum(l["team_a_goals"] for l in match["legs"])
                        total_b = sum(l["team_b_goals"] for l in match["legs"])
                        match["aggregate_team_a_goals"] = total_a
                        match["aggregate_team_b_goals"] = total_b
                        team_a_name = leg["team_a"]["name"]
                        team_b_name = leg["team_b"]["name"]
                        self.finalize_match_result(team_a_name, team_b_name,total_a,total_b,match)
                else:
                    if match["status"] != "complete":
                        self.finalize_match_result(team_a,team_b,goals_a,goals_b,match)

            all_matches_complete = all(m.get("status") == "complete" for m in current_round["matches"])

            if all_matches_complete:
                next_round = next((r for r in rounds if r["round_number"] == round_number + 1),None)
                if next_round:
                    for match in next_round["matches"]:
                        if "legs" in match:
                            for leg in match["legs"]:
                                for side in ["team_a", "team_b"]:
                                    participant = leg[side]
                                    if isinstance(participant, dict) and participant.get("source_match"):
                                        source_id = participant["source_match"]
                                        source_match = next((m for m in current_round["matches"] if m["match_id"] == source_id),None)
                                        if source_match:
                                            participant["name"] = source_match["winner"]
                        else:
                            for side in ["team_a", "team_b"]:
                                participant = match.get(side) 
                                if isinstance(participant, dict) and participant.get("source_match"):
                                    source_id = participant["source_match"]
                                    source_match = next((m for m in current_round["matches"] if m["match_id"] == source_id),None)
                                    if source_match:
                                        participant["name"] = source_match["winner"]
            
        except Exception as e:
           ErrorHandler().handle(e,context=f'failed to update knouckout for {round_number} in {self.tour_name}')
        finally:
            return self.match_data
    
    #                                cup with groups                               #
    # ============================================================================ #
    def make_groups_stages(self) -> Dict:
        """
        Organizes teams into group stages and sets up initial fixtures for each group
        in preparation for a knockout stage tournament structure.

        Returns:
            dict: The full match data including group fixtures.
        """
        try:
            if not self.teams:
                return {}

            MIN_GROUP_SIZE = 4
            total_teams = len(self.teams)

            groups_count = total_teams // MIN_GROUP_SIZE
            if total_teams % MIN_GROUP_SIZE != 0:
                groups_count += 1

            random.shuffle(self.teams)
            base_group_size = total_teams // groups_count
            remainder = total_teams % groups_count

            groups = {}
            group_matches = {}
            index = 0

            for i in range(groups_count):
                group_name = f"Group {chr(65 + i)}"
                extra = 1 if remainder > 0 else 0
                group_size = base_group_size + extra
                groups[group_name] = self.teams[index: index + group_size]
                index += group_size
                remainder -= 1 if remainder > 0 else 0

                group_manager = TourManager(self.match_data, groups[group_name], "league",self.home_or_away)
                group_matches[group_name] = group_manager.make_league()

            self.match_data = {
                "group_stages": group_matches
            }

            
        except Exception as e:
            ErrorHandler().handle(e,context='Falied to make ko groups')
        finally:
            return self.match_data
    
    def update_groups_stages(self, round_number, match_results) -> Dict:
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
            dict: The full match data including group fixtures. Updated from "match_results"
        """
        try:
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
                    if match and  match['status'] != "complete":
                        match["team_a_goals"] = team_a_goals
                        match["team_b_goals"] = team_b_goals
                        self.finalize_match_result(team_a,team_b,team_a_goals,team_b_goals,match,group_data=group_data)
            all_matches_complete = True
            for groups in self.match_data["group_stages"].values():
                for round in groups["fixtures"].values():
                    for match in round:
                        if match['status']!= 'complete':
                            all_matches_complete = False
                            break
                    

            if all_matches_complete:
                teams_to_advance = self.teams_to_advance if self.teams_to_advance else 2
                for groups in self.match_data["group_stages"].values():
                    rankings = list(groups["table"].keys())
                    next_round_players.extend(rankings[:teams_to_advance])#teams are sorted before hand
                self.make_knockout(next_round_players)
        except Exception as e:
            ErrorHandler().handle(e,context=f"Failed to update the group stage for {round_number} in {self.tour_name}") 
        finally: 
            return self.match_data
    
    def update_group_knouckout_table(self, team, goals_scored, goals_conceded, result_type,group_data):
        """
        Update the group knockout table for a team based on match result.

        Args:
            team (str): Team name.
            goals_scored (int): Goals scored by the team.
            goals_conceded (int): Goals conceded by the team.
            group_data (dict): Group data containing the table.
            result_type (str): "win", "draw", or "loss".
            
        Returns:
            None: Updates the group table in place.
        """
        try:
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
        except Exception as e:
            ErrorHandler().handle(e,context=f"Failed to update grp_ko for {self.tour_name}")
     
    def update_knockout_stage(self, round_number, match_results):
        """
        Updates knockout matches with results and progresses to the next round.

        Args:
            round_number (int): The round number to update (1-based index).
            match_results (List[Dict]): List of result dictionaries, each containing:
                - "team_a" (str): Name of team A.
                - "team_b" (str): Name of team B.
                - "team_a_goals" (int): Goals scored by team A.
                - "team_b_goals" (int): Goals scored by team B.

        Returns:
            dict: Updated match_data with knockout fixtures and table info.
        """
        try:
            rounds = self.match_data["knock_outs"].get("rounds", [])
            current_round = next(
                (r for r in rounds if r["round_number"] == round_number), None
            )
            
            next_round_players = []
            for result in match_results:
                
                team_a = result["team_a"]
                team_b = result["team_b"]
                goals_a = result["team_a_goals"]
                goals_b = result["team_b_goals"]
                # Find the match using team names
                match = next(
                    (m for m in current_round['matches'] if (m["team_a"] == team_a and m["team_b"] == team_b) or (m["team_a"] == team_b and m["team_b"] == team_a)),
                    None
                )
                if match['status'] !="complete":
                    match["team_a_goals"] = goals_a
                    match["team_b_goals"] = goals_b
                    self.finalize_match_result(team_a,team_b,goals_a,goals_b,match)
                    
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
            all_matches_complete = all(match.get('status') == 'complete'  for groups in self.match_data["group_stages"].values() for round in groups["fixtures"].values() for match in round )
            if all_matches_complete:
                teams_to_advance = self.teams_to_advance if self.teams_to_advance else 2
                for groups in self.match_data["group_stages"].values():
                    rankings = list(groups["table"].keys())
                    next_round_players.extend(rankings[:teams_to_advance])
                self.make_knockout(next_round_players) 
        except Exception as e:
            ErrorHandler().handle(e,context=f"Failed to update ko stage round {round_number} for {self.tour_name}")
        finally:
            return self.match_data

    # ============================================================================ #
    #                                Init for tours                                #
    # ============================================================================ #
    def create_tournament(self):
        """
        Creates the specified tournament type.

        Returns:
            dict: The tournament data structure.

        Raises:
            ValueError: If the tournament type is unknown.
        """
        if self.tournament_type == "league":
            return self.make_league()
        elif self.tournament_type == "cup":
            return self.make_knockout()
        elif self.tournament_type == "groups_knockout":
            return self.make_groups_stages()
        else:
            raise ValueError(f"Unknown tournament type: {self.tournament_type}")
        
        
    # ============================================================================ #
    #                       stat update for clans and players                      #
    # ============================================================================ #
    def get_player_stats(self, winner_name, loser_name):
        """Fetch PlayerStats instances for both winner and loser.
        Args:
            winner_name (str): Username of the winner.
            loser_name (str): Username of the loser.

        Returns:
            tuple: (winner_stats, loser_stats) if found, otherwise (None, None).
        """
        try:
            winner = User.objects.get(username__iexact=winner_name)
            loser = User.objects.get(username__iexact=loser_name)
            if winner and loser:
                winner_stats = winner.profile.stats
                loser_stats = loser.profile.stats
                if winner_stats and loser_stats:
                    return winner_stats, loser_stats
        except Http404:
            return None, None
        except Exception as e:
            ErrorHandler().handle(e,context="Failed to get player stats")
            return None, None
    
    def get_clan_stats(self,winner_name, loser_name):
        """Fetch ClanStats instances for both winner and loser.
        Args:
        winner_name (str): Username of the winner.
        loser_name (str): Username of the loser.

        Returns:
            tuple: (winner_stats, loser_stats) if found, otherwise (None, None).
        """
        try:
            winner = get_object_or_404(Clans, clan_name=winner_name)
            loser = get_object_or_404(Clans, clan_name=loser_name)
            if winner and loser:
                return winner.stat, loser.stat
        except Http404: #fails silently if clan not found might be a user
            return None, None
        except Exception as e:
            ErrorHandler().handle(e,context="Failed to get clan stats")
            return None, None
        
    def store_records(self, winner_name, loser_name, winner_goals, loser_goals, result_type):
        """
        Update and store  records for the match result.

        Args:
            winner_name (str): The profile of the winning team.
            loser_name (str): The profile of the losing team.
            winner_goals (int): Goals scored by the winner.
            loser_goals (int): Goals scored by the loser.
            result_type (str): Type of result ('win', 'draw').
        """

        
        winner_stats, loser_stats = self.get_player_stats(winner_name, loser_name) 

        if winner_stats is None or loser_stats is None:
            winner_stats, loser_stats = self.get_clan_stats(winner_name, loser_name)
        

        if winner_stats is None or loser_stats is None:
            ErrorHandler().handle(Exception("Could not find stats for winner or loser"), context="Failed to store records")
            return

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
            "opponent": loser_name,  
            "result": winner_result, 
            "score": f"{winner_goals}:{loser_goals}"
        }
        loser_entry = {
            "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tour_name":self.tour_name,   
            "opponent": winner_name,  
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

    def get_player_elo_and_instance(self,name):
        """
        Fetch the Elo rating and stats instance for a player by username.

        Args:
            name (str): Username of the player.

        Returns:
            tuple: (elo_rating (float or int), stats instance) or (None, None) if not found.
        """
        try:
            player = User.objects.get(username__iexact=name)
            instance = player.profile.stats
            return instance.elo_rating, instance    
        except Exception as e:
            ErrorHandler().handle(e,context="Failed to get player elo")
            return None, None

    def get_clan_elo_and_instance(self,name):
        """
        Fetch the Elo rating and stats instance for a clan by clan_name.

        Args:
            name (str): Clan name.

        Returns:
            tuple: (elo_rating (float or int), stats instance) or (None, None) if not found.
        """
        try:
            clan = Clans.objects.get(clan_name=name)
            instance = clan.stat
            return instance.elo_rating, instance
        except Clans.DoesNotExist as e:
            ErrorHandler().handle(e, context="Failed to get clan elo")
            return None, None
        
    def update_elo(self,winner_elo, loser_elo, k):
        """
        Calculate new Elo ratings for winner and loser.

        Args:
            winner_elo (float): Current Elo rating of the winner.
            loser_elo (float): Current Elo rating of the loser.
            k (float): The K-factor (maximum rating adjustment).

        Returns:
            tuple: (winner_new_elo, loser_new_elo) or (None, None) if error occurs.
        """
        try:
            expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
            winner_new_elo = winner_elo + k * (1 - expected_winner)
            loser_new_elo = loser_elo - k * (1 - expected_winner)
            return winner_new_elo, loser_new_elo
        except Exception as e:
            ErrorHandler().handle(e, context="Failed to update Elo ratings")
            return None, None
    
    def update_elo_for_match(self,winner_name, loser_name, k=32):
        """
        Update Elo ratings for a match.

        Args:
            winner_name (str): Name of the winner (player or clan).
            loser_name (str): Name of the loser (player or clan).
            k (int): The K-factor for Elo calculation (default: 32).

        Returns:
            None: Updates the database directly.
        """
        
        winner_elo, winner_instance = self.get_player_elo_and_instance(winner_name)
        loser_elo, loser_instance = self.get_player_elo_and_instance(loser_name)
        
        if winner_elo is None or loser_elo is None:
            winner_elo, winner_instance = self.get_clan_elo_and_instance(winner_name)
            loser_elo, loser_instance = self.get_clan_elo_and_instance(loser_name)
            
        winner_new_elo, loser_new_elo = self.update_elo(winner_elo, loser_elo, k)
        if winner_instance and loser_instance:
            winner_instance.elo_rating = winner_new_elo
            winner_instance.save()
            winner_instance.set_rank_based_on_elo()
           
            loser_instance.elo_rating = loser_new_elo
            loser_instance.save()
            loser_instance.set_rank_based_on_elo()

    def update_team_db_stats(self,team_a,team_b,goals_a, goals_b):
        """
        Update clan statistics for two teams based on match results.
        
        Args:
            team_a (str): Name or identifier of team A.
            team_b (str): Name or identifier of team B.
            goals_a (int): Goals scored by team A.
            goals_b (int): Goals scored by team B.
        """
       
        try:
            team_a_stat, team_b_stat = self.get_clan_stats(team_a, team_b)
            print(f"Updating stats for {team_a} vs {team_b}: {goals_a}-{goals_b}")
            if team_a_stat is None or team_b_stat is None:
                print(f"Stats not found for {team_a} or {team_b}, fetching player stats.")
                # Fallback to player stats if clan stats are not available
                team_a_stat, team_b_stat = self.get_player_stats(team_a, team_b)
                if team_a_stat is None or team_b_stat is None:
                    print(f"Player stats not found for {team_a} or {team_b}. Cannot update stats.")
                    return   
            if goals_a > goals_b:
                result_a, result_b = "win", "loss"
            elif goals_a < goals_b:
                result_a, result_b = "loss", "win"
            else:
                result_a, result_b = "draw", "draw"
            
            for stat, gf, ga, result_type in [
                            (team_a_stat, goals_a, goals_b, result_a),
                            (team_b_stat, goals_b, goals_a, result_b)
                        ]:
                stat.gd += gf-ga
                stat.gf += gf
                stat.ga += ga
                stat.total_matches += 1
                if result_type == "win":
                    stat.total_wins += 1
                elif result_type == "loss":
                    stat.total_losses += 1
                else:
                    stat.total_draws += 1
                win_rate = ((stat.total_wins + stat.total_draws/2) / stat.total_matches) * 100 if stat.total_matches > 0 else 0
                stat.win_rate = round(win_rate,3)
                stat.save()
        except Exception as e:
            ErrorHandler().handle(e,context="Failed to update team DB stats")

    def finalize_match_result(self, team_a, team_b, goals_a, goals_b, match, group_data=None):
        """
        Finalize the result of a match and update standings if applicable.
        
        Args:
            team_a (str): Name of Team A
            team_b (str): Name of Team B
            goals_a (int): Goals scored by Team A
            goals_b (int): Goals scored by Team B
            match (dict): Match data dictionary
            group_data (dict): Optional group table/standings to update
        """
        if goals_a > goals_b:
            winner, loser = team_a, team_b
            winner_goals, loser_goals = goals_a, goals_b
            self._handle_result(winner, loser, winner_goals, loser_goals,group_data)
            match["winner"] = winner
        elif goals_a < goals_b:
            winner, loser = team_b, team_a
            winner_goals, loser_goals = goals_b, goals_a
            self._handle_result(winner, loser, winner_goals, loser_goals,group_data)
            match["winner"] = winner
        else:
            self._handle_draw(team_a, team_b, goals_a, goals_b,group_data)
            match["winner"] = "Draw"
        match["team_a_goals"] = goals_a
        match["team_b_goals"] = goals_b
        match["status"] = "complete"
        
    def update_table(self, team, goals_scored, goals_conceded, result_type):
        """
        Updates the league table for a given team after a match.

        Args:
            team (str): The team name.
            goals_scored (int): Goals scored by the team in the match.
            goals_conceded (int): Goals conceded by the team in the match.
            result_type (str): "win", "draw", or "loss".

        Notes:
            - Initializes a team's stats if not already in the table.
            - Updates goals, points, and match results.
            - Sorts the table by points, goal difference, wins, then goals scored.
        """
        table = self.match_data.get("table")
        if table:
            if team not in table:
                    table[team] = {
                        "goals_scored": 0,
                        "goals_conceded": 0,
                        "goal_difference": 0,
                        "points": 0,
                        "matches_played": 0,
                        "wins": 0,
                        "draws": 0,
                        "losses": 0,
                    }
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
            reverse=True 
            )
        

            self.match_data["table"] = {team[0]: team[1] for team in sorted_table}
        

    def _handle_result(self, winner, loser, winner_goals, loser_goals,group_data=None):
        """
        Handles post-match updates when there is a winner.

        Args:
            winner (str): Name of the winning team.
            loser (str): Name of the losing team.
            winner_goals (int): Goals scored by the winner.
            loser_goals (int): Goals scored by the loser.
            group_data (dict, optional): Group/knockout table to update, if applicable.
        """
        # Update ELO rating for winner and loser
        self.update_elo_for_match(winner, loser)
        
        # Update match results in the league table and group/knockout table
        self.update_table(winner, winner_goals, loser_goals, result_type="win")
        self.update_table(loser, loser_goals, winner_goals, result_type="loss")
        
        # Update group/knockout table if provided
        if group_data:
            self.update_group_knouckout_table(winner, winner_goals, loser_goals,group_data=group_data, result_type="win")
            self.update_group_knouckout_table(loser, loser_goals, winner_goals,group_data=group_data,result_type="loss")
            
        # Store match records for both teams
        self.store_records(winner, loser, winner_goals, loser_goals,result_type="win")
        
        # Update database statistics for the teams
        self.update_team_db_stats(team_a=winner,team_b=loser, goals_a=winner_goals, goals_b=loser_goals)

    def _handle_draw(self, team_a, team_b, goals_a, goals_b,group_data=None):
        """
        Handles post-match updates when the match ends in a draw.

        Args:
            team_a (str): Name of Team A.
            team_b (str): Name of Team B.
            goals_a (int): Goals scored by Team A.
            goals_b (int): Goals scored by Team B.
            group_data (dict, optional): Group/knockout table to update, if applicable.
        """
        # Update league table for both teams
        self.update_table(team_a, goals_a, goals_b, result_type="draw")
        self.update_table(team_b, goals_b, goals_a, result_type="draw")
        
        # If in a group/knockout stage, also update that table
        if group_data:
            self.update_group_knouckout_table(team_a, goals_a, goals_b,group_data=group_data, result_type="draw")
            self.update_group_knouckout_table(team_b, goals_b, goals_a,group_data=group_data, result_type="draw")
        # Store match record for history/statistics
        self.store_records(team_a, team_b, goals_a, goals_b, result_type="draw")
        
        # Update database statistics for the teams
        self.update_team_db_stats(team_a,team_b,goals_a, goals_b)

