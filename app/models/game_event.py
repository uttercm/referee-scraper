from pytz import timezone


class GameEvent:
    def __init__(
        self,
        league,
        level,
        date_time,
        location,
        home_team,
        away_team,
        ref_crew,
        is_cancelled=False,
    ):
        self.date_time = date_time.astimezone(timezone("US/Eastern"))
        self.location = location
        self.home_team = home_team
        self.away_team = away_team
        self.ref_crew = ref_crew
        self.is_cancelled = is_cancelled
        self.description = "{} vs {}".format(home_team, away_team)
        self.summary = "{} {}".format(league, level)

    def is_my_game(self):
        return self.ref_crew.get_my_position() is not None
