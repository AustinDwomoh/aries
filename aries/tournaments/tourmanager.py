import random
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
        
        # Update the match results for the round
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
        self.match_data = {}  
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
    def make_groups_knockout(self, groups_count):
        """Creates a groups + knockout structure."""
       
        groups = {}
        group_size = len(self.teams) // groups_count
        for i in range(groups_count):
            group_name = f"Group {chr(65 + i)}"
            groups[group_name] = self.teams[i * group_size:(i + 1) * group_size]

        group_matches = {}
        for group_name, group_teams in groups.items():
            group_manager = TourManager(self.match_data, group_teams, "league")
            group_matches[group_name] = group_manager.make_league()
            
        self.match_data["groups_knockout"] = {
            "groups": group_matches,
        }
        return self.match_data["groups_knockout"]

    def continue_groups_knockout(self):
        top_teams = []
        for group_matches in self.match_data["groups_knockout"]["groups"].values():
            group_results = sorted(
                group_matches,
                key=lambda match: match["team_a_goals"] + match["team_b_goals"],
                reverse=True,
            )
            top_teams.append(group_results[0]["team_a"])  # Assuming team_a leads the group
        knockout_manager = TourManager(self.match_data, top_teams, "knockout")
        knockout_matches = knockout_manager.make_knockout()
        self.match_data["groups_knockout"]["knockout"] = knockout_matches
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
       
