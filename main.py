from typing import Optional
from flask import Flask, request
from flask_cors import CORS
from pysmashgg import SmashGG

STARTGG_ENDPOINT = 'https://api.start.gg/gql/alpha'
STARTGG_TOKEN = '4bc70a02bdf40fff325f20ef90cfa690'

application = Flask(__name__)

cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'

MATCHES_MAP = {
    "A": "match_1",
    "B": "match_2",
    "C": "match_3",
    "D": "match_4",
    "E": "match_1",
    "F": "match_2",
    "G": "match_1",
    "H": "match_1",
    "I": "match_1",
    "J": "match_1",
    "K": "match_2",
    "L": "match_1",
    "M": "match_2",
    "N": "match_1",
    "O": "match_1",
}


def get_tag_by_name(name: str) -> str:
    if name:
        name = name.upper()
    else:
        return ""

    if name == "Vermi_CL".upper():
        return "Aracne"
    elif name == "GrayFokxx".upper():
        return "TEW"
    elif name == "Raz".upper():
        return "RFL"
    elif name in ["Whisp".upper(), "Eury".upper(), "Snow".upper()]:
        return "WG"
    return ""

def get_score(standing) -> Optional[int]:
    if standing:
        return standing["stats"]["score"]["value"]





@application.route('/bracket')
def bracket():
    smash = SmashGG(STARTGG_TOKEN, True)
    bracket_sets = smash.bracket_show_sets(2466677, 1)

    matches = {
        "winners_quarter_finals": {
            "match_1": None,
            "match_2": None,
            "match_3": None,
            "match_4": None,
        },
        "winners_semi_finals": {
            "match_1": None,
            "match_2": None,
        },
        "winners_final": {
            "match_1": None,
        },
        "grand_final": {
            "match_1": None,
        },
        "grand_final_reset": {
            "match_1": None,
        },
        "losers_round_1": {
            "match_1": None,
            "match_2": None,
        },
        "losers_quarter_final": {
            "match_1": None,
            "match_2": None,
        },
        "losers_semi_final": {
            "match_1": None,
        },
        "losers_final": {
            "match_1": None,
        }
    }
    try:
        for node in bracket_sets:
            p1_name, p1_tag, p1_score, p2_name, p2_tag, p2_score = (None, None, None, None, None, None)
            if 'entrant1Name' in node.keys():
                p1_name = node["entrant1Name"]
            p1_tag = get_tag_by_name(p1_name)
            if 'entrant1Score' in node.keys():
                p1_score = node["entrant1Score"]
            if 'entrant2Name' in node.keys():
                p2_name = node["entrant2Name"]
            p2_tag = get_tag_by_name(p2_name)
            if 'entrant2Score' in node.keys():
                p2_score = node["entrant2Score"]
            match = {
                "player_1": {
                    "tag": p1_tag if p1_tag else "",
                    "name": p1_name if p1_name else "",
                    "score": p1_score if p1_score and p1_score > 0 else 0
                },
                "player_2": {
                    "tag": p2_tag if p2_tag else "",
                    "name": p2_name if p2_name else "",
                    "score": p2_score if p2_score and p2_score > 0 else 0
                }
            }
            round_name = node["fullRoundText"]
            if round_name in ["Winners Quarter-Final", "Winners Round 1"]:
                matches["winners_quarter_finals"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name == "Winners Semi-Final":
                matches["winners_semi_finals"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name == "Winners Final":
                matches["winners_final"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name == "Grand Final":
                matches["grand_final"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name == "Grand Final Reset":
                matches["grand_final_reset"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name == "Losers Round 1":
                matches["losers_round_1"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name in ["Losers Quarter-Final", "Losers Round 2"]:
                matches["losers_quarter_final"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name == "Losers Semi-Final":
                matches["losers_semi_final"][MATCHES_MAP[node["identifier"]]] = match
            elif round_name == "Losers Final":
                matches["losers_final"][MATCHES_MAP[node["identifier"]]] = match
    except Exception as e:
        print(e)

    return matches
