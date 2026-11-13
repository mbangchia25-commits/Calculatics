import os
import json
import math
import urllib3
import requests
from datetime import datetime, timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = os.environ.get("FOOTBALL_API_KEY")
HEADERS = {"X-Auth-Token": API_KEY}
URL = "https://football-data.org"

def poisson_probability(lmbda, k):
    return (lmbda ** k * math.exp(-lmbda)) / math.factorial(k)

def calculate_forecast(home_xg=1.45, away_xg=1.15):
    home_win, draw, away_win = 0.0, 0.0, 0.0
    for h in range(6):
        for a in range(6):
            prob = poisson_probability(home_xg, h) * poisson_probability(away_xg, a)
            if h > a:
                home_win += prob
            elif h == a:
                draw += prob
            else:
                away_win += prob
    return {
        "home_prob": round(home_win * 100),
        "draw_prob": round(draw * 100),
        "away_prob": round(away_win * 100),
        "tip": "1" if home_win > max(draw, away_win) else ("2" if away_win > draw else "X")
    }

def main():
    response = requests.get(URL, headers=HEADERS, verify=False)
    data = response.json()
    matches_output = []

    for match in data.get("matches", []):
        forecast = calculate_forecast(home_xg=1.5, away_xg=1.1)
        matches_output.append({
            "id": match["id"],
            "competition": match["competition"]["name"],
            "utcDate": match["utcDate"],
            "status": match["status"],
            "homeTeam": match["homeTeam"].get("shortName") or match["homeTeam"]["name"],
            "awayTeam": match["awayTeam"].get("shortName") or match["awayTeam"]["name"],
            "score": match["score"]["fullTime"],
            "forecast": forecast
        })

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "matches": matches_output
    }

    with open("forecasts.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
