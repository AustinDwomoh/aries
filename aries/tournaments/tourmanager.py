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

    def make_league(self):
        """Creates a round-robin structure for leagues."""
        matches = []
        round_number = 1

        for i, team_a in enumerate(self.teams):
            for team_b in self.teams[i + 1:]:
                match = {
                    "round": f"R{round_number}",
                    "team_a": team_a,
                    "team_b": team_b,
                    "team_a_goals": 0,
                    "team_b_goals": 0,
                }
                matches.append(match)
                round_number += 1

        self.match_data["league"] = matches
        return matches

    def make_knockout(self):
        """Creates a knockout structure for cups."""
        teams = self.teams.copy()
        if len(teams) % 2 != 0:
            teams.append("Bye")  # Add a bye if the number of teams is odd

        matches = []
        round_number = 1

        while len(teams) > 1:
            round_name = f"Round {round_number}"
            round_matches = []
            for i in range(len(teams) // 2):
                match = {
                    "team_a": teams[i],
                    "team_b": teams[len(teams) - i - 1],
                    "team_a_goals": 0,
                    "team_b_goals": 0,
                }
                round_matches.append(match)
            matches.append({"round": round_name, "matches": round_matches})

            # Placeholder logic for determining winners
            teams = [
                match["team_a"] if match["team_a_goals"] >= match["team_b_goals"] else match["team_b"]
                for match in round_matches if "Bye" not in [match["team_a"], match["team_b"]]
            ]
            round_number += 1

        self.match_data["knockout"] = matches
        return matches

    def make_league_knockout(self):
        """Creates a combined league and knockout structure."""
        # Step 1: Create a league (round-robin) phase
        league_matches = self.make_league()

        # Step 2: Take top teams (e.g., top 4) for knockout phase
        top_teams = self.teams[:4]  # Placeholder: Adjust based on league results
        knockout_manager = TourManager(self.match_data, top_teams, "knockout")
        knockout_matches = knockout_manager.make_knockout()

        self.match_data["league_knockout"] = {
            "league": league_matches,
            "knockout": knockout_matches,
        }
        return self.match_data["league_knockout"]

    def make_groups_knockout(self, groups_count=2):
        """Creates a groups + knockout structure."""
        # Step 1: Divide teams into groups
        groups = {}
        group_size = len(self.teams) // groups_count
        for i in range(groups_count):
            group_name = f"Group {chr(65 + i)}"
            groups[group_name] = self.teams[i * group_size:(i + 1) * group_size]

        group_matches = {}
        for group_name, group_teams in groups.items():
            group_manager = TourManager(self.match_data, group_teams, "league")
            group_matches[group_name] = group_manager.make_league()

        # Step 2: Take top teams from each group for knockout phase
        knockout_teams = [group[0] for group in groups.values()]  # Placeholder: Adjust based on group results
        knockout_manager = TourManager(self.match_data, knockout_teams, "knockout")
        knockout_matches = knockout_manager.make_knockout()

        self.match_data["groups_knockout"] = {
            "groups": group_matches,
            "knockout": knockout_matches,
        }
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
