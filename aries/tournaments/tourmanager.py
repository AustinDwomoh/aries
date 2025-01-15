import random
from typing import List,Dict
class TourManager:
    def __init__(self, json_data, teams_names, tournament_type):
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
# ============================================================================ #
#                                    leagues                                   #
# ============================================================================ #
    def make_league(self):
        """Creates a round-robin structure for leagues."""
        if len(self.teams) % 2 == 1:
            self.teams.append("Bye")  # Add a dummy team for odd number of teams

        n = len(self.teams)
        round_robin_fixtures = {}

        # Round-robin scheduling
        for round_number in range(n - 1):
            round_matches = []
            for i in range(n // 2):
                home = self.teams[i]
                away = self.teams[n - 1 - i]
                round_matches.append({
                    "match":i+1,
                    "team_a": home,
                    "team_b": away,
                    "team_a_goals": None,
                    "team_b_goals": None,
                    "winner": None
                })

            
            round_robin_fixtures[f"round_{round_number + 1}"] = round_matches
            print(f"Round {round_number + 1} Matches: {round_matches}")
            
            # Rotate teams (except the first one) to generate new pairs
            self.teams.insert(1, self.teams.pop())
        print(round_robin_fixtures)
        return round_robin_fixtures

    def update_league(self,round_number,match_results):
        round_key = f"round_{round_number}"
        if round_key not in self.match_data['matches']:
            return
        round_matches = self.match_data['matches'][round_key]
        for result in match_results:
            match_number = result["match"]
            match = next((m for m in round_matches if m["match"] == match_number), None)
            if match:
                match["team_a_goals"] = result["team_a_goals"]
                match["team_b_goals"] = result["team_b_goals"]
                
                if match["team_a_goals"] > match["team_b_goals"]:
                    match["winner"] = match["team_a"]
                elif match["team_a_goals"] < match["team_b_goals"]:
                    match["winner"] = match["team_b"]
                else:
                    match["winner"] = "Draw"  
        return self.match_data['matches'][round_key]
# ============================================================================ #
#                                   knockouts                                  #
# ============================================================================ #
    def make_knockout(self,players =None):
        """Creates a knockout structure for cups."""
        if players:
            teams = players
        else:
            teams = self.teams.copy()
        random.shuffle(teams)  
        knockout_matches = [] 
        i = 0
        while len(teams) > 1:
            round_matches = [] 
            team_a = teams.pop(0)
            team_b = teams.pop(0)
            match = {
                "team_a": team_a,
                "team_b": team_b,
                "team_a_goals": None,
                "team_b_goals": None,
                "winner": None
            }
            round_matches.append(match)
            knockout_matches.append({f"matches_{i}": round_matches})
            i += 1
        self.match_data["knockout"] = knockout_matches
        return knockout_matches

    def update_knockout(self):
        knockout_matches = [match for round_matches in self.match_data["knockout"] for match in round_matches.values()]
        next_round_teams = []
        for round_matches in knockout_matches:
            for match in round_matches:
                if match["team_a_goals"] > match["team_b_goals"]:
                    match["winner"] = match["team_a"]
                elif match["team_a_goals"] < match["team_b_goals"]:
                    match["winner"] = match["team_b"]
                else:
                    match["winner"] = None 
                if match["winner"]:
                    next_round_teams.append(match["winner"])
        self.match_data["knockout"] = {}
        self.make_knockout(next_round_teams)

    # ============================================================================ #
    #                              leage and knockout                              #
    # ============================================================================ #
    def make_league_knockout(self):
        """Creates a combined league and knockout structure."""
        league_matches = self.make_league()
        
        self.match_data["league_knockout"] = {
            "league": league_matches,
        }
        return self.match_data["league_knockout"]
    
    def continue_league_knockout(self, num):
        league_results = sorted(
            self.match_data["league"],
            key=lambda match: match["team_a_goals"] + match["team_b_goals"],
            reverse=True,
        )
        top_teams = [match["team_a"] for match in league_results[:num]]
        knockout_manager = TourManager(self.match_data, top_teams, "knockout")
        knockout_matches = knockout_manager.make_knockout()
        self.match_data["league_knockout"]["knockout"] = knockout_matches
        return self.match_data["league_knockout"]
# ============================================================================ #
#                                cup with groups                               #
# ============================================================================ #
    def make_groups_knockout(self, groups_count: int =None) -> Dict:
        """Creates a groups + knockout structure."""
        groups_count = 1
        self.teams = ['1', '2', '3','4']  # Example teams; replace with dynamic list
        groups = {}
        group_size = len(self.teams) // groups_count
        remainder = len(self.teams) % groups_count

        # Distribute teams into groups
        start_index = 0
        for i in range(groups_count):
            group_name = f"Group {chr(65 + i)}"
            end_index = start_index + group_size + (1 if remainder > 0 else 0)
            groups[group_name] = self.teams[start_index:end_index]
            start_index = end_index
            if remainder > 0:
                remainder -= 1

        group_matches = {}
        for group_name, group_teams in groups.items():
            group_manager = TourManager(self.match_data, group_teams, "league")
            group_matches[group_name] = group_manager.make_league()

        self.match_data["groups_knockout"] = {
            "groups": group_matches,
        }
        return self.match_data["groups_knockout"]
   
    def update_groups_knockout(self, round_number: int, group: int, match_results) -> None:
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
        round_key = f"round_{round_number}"
        groups_knockout = self.match_data.get('groups_knockout', {})
        groups = groups_knockout.get("groups", {})
        group_matches = groups[group]
        round_matches = group_matches[round_key]
        for result in match_results:
            match_number = result.get("match")
            team_a_goals = result.get("team_a_goals")
            team_b_goals = result.get("team_b_goals")
            match = next((m for m in round_matches if m["match"] == match_number), None)
            match["team_a_goals"] = team_a_goals
            match["team_b_goals"] = team_b_goals
            if team_a_goals > team_b_goals:
                match["winner"] = match["team_a"]
            elif team_a_goals < team_b_goals:
                match["winner"] = match["team_b"]
            else:
                match["winner"] = "Draw"
        self._update_standings(group)

    def _update_standings(self, group: str, teams_per_group: int) -> None:
        """
        Updates standings (points and goal difference) for a specific group.
        If all group matches are completed, proceeds to the knockout stage.

        Args:
            group (str): The group identifier.
            teams_per_group (int): The number of top teams to advance to the knockout stage.

        Returns:
            dict: Updated match data with standings and knockout phase details.
        """
        # Check if all matches are completed before proceeding
        all_matches_completed = True
        for group_name, group_matches in self.match_data["groups_knockout"]["groups"].items():
            for round_matches in group_matches.values():  # Iterate through rounds
                for match in round_matches:  # Check each match
                    if match["team_a_goals"] is None or match["team_b_goals"] is None:
                        all_matches_completed = False
                        print(f"Incomplete match detected in group '{group_name}'. Cannot proceed to knockouts.")
                        break
                if not all_matches_completed:
                    break
            if not all_matches_completed:
                break

        if not all_matches_completed:
            return self.match_data["groups_knockout"]

        # Calculate team points and goal differences after confirming all matches are completed
        group_matches = self.match_data["groups_knockout"]["groups"].get(group, {})
        team_points = {}

        for round_matches in group_matches.values():
            for match in round_matches:
                for team, goals in [(match["team_a"], match["team_a_goals"]), (match["team_b"], match["team_b_goals"])]:
                    team_points.setdefault(team, {"points": 0, "goal_difference": 0})
                    opponent_goals = match["team_b_goals"] if team == match["team_a"] else match["team_a_goals"]
                    if goals > opponent_goals:
                        team_points[team]["points"] += 3
                    elif goals == opponent_goals:
                        team_points[team]["points"] += 1
                    team_points[team]["goal_difference"] += goals - opponent_goals

        # Sort teams based on points and goal difference
        sorted_teams = sorted(
            team_points.items(),
            key=lambda item: (item[1]["points"], item[1]["goal_difference"]),
            reverse=True,
        )
        top_teams = [team for team, _ in sorted_teams[:teams_per_group]]

        # Proceed to knockout stage
        knockout_manager = TourManager(self.match_data, top_teams, "knockout")
        knockout_matches = knockout_manager.make_knockout()
        self.match_data["groups_knockout"]["knockout"] = knockout_matches
        print("All group matches are completed. Knockout phase generated successfully.")

        # Save updated standings
        self.match_data["groups_knockout"]["standings"] = team_points

        return self.match_data["groups_knockout"]



    def create_tournament(self):
        """Creates the specified tournament type."""
        if self.tournament_type == "league":
            return self.make_league()
        elif self.tournament_type == "cup":
            return self.make_knockout()
        elif self.tournament_type == "league_knockout":
            return self.make_league_knockout()
        elif self.tournament_type == "groups_knockout":
            return self.make_groups_knockout()
        else:
            raise ValueError(f"Unknown tournament type: {self.tournament_type}")
       
