import json
import os


def set_uploaded_activity_ids(uploaded_activity_ids):
    with open('strava_uploaded.json', "w") as f:
        json.dump(uploaded_activity_ids, f)


def get_uploaded_activity_ids():
    if not os.path.exists("strava_uploaded.json"):
        return []

    with open('strava_uploaded.json', "r") as f:
        ids = json.load(f)
    print(f"loaded data : {len(ids)}")
    return ids
