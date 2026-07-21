from django.db.models import Q
from .models import Participant, Match, MatchEvent

def calculate_standings(stage_or_tournament):
    # Determine if we received a stage or tournament
    from .models import Stage, Tournament
    
    if isinstance(stage_or_tournament, Stage):
        stage = stage_or_tournament
        tournament = stage.tournament
        participants = Participant.objects.filter(tournament=tournament)
        completed_matches = Match.objects.filter(stage=stage, status="completed")
    else:
        tournament = stage_or_tournament
        participants = Participant.objects.filter(tournament=tournament)
        completed_matches = Match.objects.filter(tournament=tournament, status="completed")

    standings = []

    for p in participants:
        played = 0
        won = 0
        drawn = 0
        lost = 0
        gf = 0
        ga = 0
        yellow_cards = 0
        red_cards = 0

        # Filter matches where this participant played
        for match in completed_matches:
            is_home = (match.home_id == p.id)
            is_away = (match.away_id == p.id)

            if is_home or is_away:
                played += 1
                hs = match.home_score if match.home_score is not None else 0
                as_ = match.away_score if match.away_score is not None else 0

                if is_home:
                    gf += hs
                    ga += as_
                    if hs > as_:
                        won += 1
                    elif hs == as_:
                        drawn += 1
                    else:
                        lost += 1
                else:
                    gf += as_
                    ga += hs
                    if as_ > hs:
                        won += 1
                    elif as_ == hs:
                        drawn += 1
                    else:
                        lost += 1

                # Calculate cards for fair play
                yellow_cards += MatchEvent.objects.filter(match=match, player=p.player, event_type="yellow_card").count()
                red_cards += MatchEvent.objects.filter(match=match, player=p.player, event_type="red_card").count()

        gd = gf - ga
        pts = (won * 3) + (drawn * 1)

        standings.append({
            "participant": p,
            "player": p.player,
            "played": played,
            "won": won,
            "drawn": drawn,
            "lost": lost,
            "gf": gf,
            "ga": ga,
            "gd": gd,
            "pts": pts,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
        })

    # Sort rules: Points -> GD -> GF -> Fewer Red Cards -> Fewer Yellow Cards -> Gamer Tag / Name
    standings.sort(key=lambda x: (
        -x["pts"],
        -x["gd"],
        -x["gf"],
        x["red_cards"],
        x["yellow_cards"],
        x["player"].gamer_tag.lower() if x["player"].gamer_tag else x["player"].name.lower()
    ))

    return standings
