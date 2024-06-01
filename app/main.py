from typing import Optional
import requests
import uvicorn

from fastapi import FastAPI

app = FastAPI()


STARTGG_ENDPOINT = 'https://api.start.gg/gql/alpha'
STARTGG_TOKEN = '4bc70a02bdf40fff325f20ef90cfa690'


def get_tag_by_name(name: str) -> str:
    name = name.upper()
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


global_winners_qf = None

@app.get('/bracket')
def bracket():
    global global_winners_qf
    print("before")
    print(global_winners_qf)
    query = """
    {
    event(slug: "tournament/raging-league/event/raging-league-final-top-8") {
        name
        sets {
        nodes {
            fullRoundText
            slots {
            entrant {
                name
            }
            standing {
                stats {
                score {
                    value
                }
                }
            }
            }
        }
        }
    }
    }
    """
    response = requests.post(
        STARTGG_ENDPOINT,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {STARTGG_TOKEN}'
        },
        json={'query': query},
        timeout=5
    )
    if response.status_code != 200:
        return {}
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
    if "data" in response.json().keys():
        nodes = response.json()["data"]["event"]["sets"]["nodes"]
        try:
            for node in nodes:
                p1_name, p1_tag, p1_score, p2_name, p2_tag, p2_score = (None, None, None, None, None, None)
                player_1 = node["slots"][0]["entrant"]
                p1_standing = node["slots"][0]["standing"]
                if player_1:
                    p1_name = player_1["name"]
                    p1_tag = get_tag_by_name(p1_name)
                    p1_score = get_score(p1_standing)

                player_2 = node["slots"][1]["entrant"]
                p2_standing = node["slots"][1]["standing"]
                if player_2:
                    p2_name = player_2["name"]
                    p2_tag = get_tag_by_name(p2_name)
                    p2_score = get_score(p2_standing)
                match = {
                    "player_1": {
                        "tag": p1_tag if p1_tag else "",
                        "name": p1_name if p1_name else "",
                        "score": p1_score if p1_score else 0
                    },
                    "player_2": {
                        "tag": p2_tag if p2_tag else "",
                        "name": p2_name if p2_name else "",
                        "score": p2_score if p2_score else 0
                    }
                }

                round_name = node["fullRoundText"]
                if round_name in ["Winners Quarter-Final", "Winners Round 1"]:
                    if global_winners_qf is not None:
                        matches["winners_quarter_finals"] = global_winners_qf
                    if matches["winners_quarter_finals"]["match_3"]:
                        matches["winners_quarter_finals"]["match_4"] = match
                        if match["player_1"]["score"] or match["player_2"]["score"]:
                            global_winners_qf = matches["winners_quarter_finals"]
                    elif matches["winners_quarter_finals"]["match_2"]:
                        matches["winners_quarter_finals"]["match_3"] = match
                    elif matches["winners_quarter_finals"]["match_1"]:
                        matches["winners_quarter_finals"]["match_2"] = match
                    else:
                        matches["winners_quarter_finals"]["match_1"] = match
                elif round_name == "Winners Semi-Final":
                    if matches["winners_semi_finals"]["match_1"]:
                        matches["winners_semi_finals"]["match_2"] = match
                    else:
                        matches["winners_semi_finals"]["match_1"] = match
                elif round_name == "Winners Final":
                    matches["winners_final"]["match_1"] = match
                elif round_name == "Grand Final":
                    matches["grand_final"]["match_1"] = match
                elif round_name == "Grand Final Reset":
                    matches["grand_final_reset"]["match_1"] = match
                elif round_name == "Losers Round 1":
                    if matches["losers_round_1"]["match_1"]:
                        matches["losers_round_1"]["match_2"] = match
                    else:
                        matches["losers_round_1"]["match_1"] = match
                elif round_name in ["Losers Quarter-Final", "Losers Round 2"]:
                    if matches["losers_quarter_final"]["match_1"]:
                        matches["losers_quarter_final"]["match_2"] = match
                    else:
                        matches["losers_quarter_final"]["match_1"] = match
                elif round_name == "Losers Semi-Final":
                    matches["losers_semi_final"]["match_1"] = match
                elif round_name == "Losers Final":
                    matches["losers_final"]["match_1"] = match
        except Exception as e:
            print(e)

    print("after")
    print(global_winners_qf)
    return matches


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
