import json
import os


def set_uploaded_activity_ids(uploaded_activity_ids):
    with open('strava_uploaded.json', "w") as f:
        json.dump(uploaded_activity_ids, f)


# 用于记录garmin导出的用活动id命名的fit/gpx文件是否上传
def get_uploaded_activity_ids():
    if not os.path.exists("strava_uploaded.json"):
        return []

    with open('strava_uploaded.json', "r") as f:
        ids = json.load(f)
    print(f"loaded data : {len(ids)}")
    return ids


# 用于记录nrc导出的用timestamp命名的gpx文件是否上传
def get_uploaded_nrc_timestamps():
    if not os.path.exists("nrc_uploaded.json"):
        return []

    with open('nrc_uploaded.json', "r") as f:
        ids = json.load(f)
    print(f"loaded data : {len(ids)}")
    return ids


def set_uploaded_nrc_timestamps(timestamps):
    with open('nrc_uploaded.json', "w") as f:
        json.dump(timestamps, f)
