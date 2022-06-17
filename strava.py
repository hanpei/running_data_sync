import argparse
import json
import logging
import os
import time
from stravalib.client import Client
from stravalib.util.limiter import RateLimiter, XRateLimitRule
from garmin import make_garmin_client
from utils import get_uploaded_activity_ids, set_uploaded_activity_ids

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_strava_client(client_id, client_secret, refresh_token):

    rate_limiter = RateLimiter()
    rate_limiter.rules.append(XRateLimitRule(
        {'short': {'usageFieldIndex': 0, 'usage': 0,
                   # 60s * 15 = 15 min
                   'limit': 100, 'time': (60*15),
                   'lastExceeded': None, },
         'long': {'usageFieldIndex': 1, 'usage': 0,
                  # 60s * 60m * 24 = 1 day
                  'limit': 1000, 'time': (60*60*24),
                  'lastExceeded': None}}))
    client = Client(rate_limiter=rate_limiter)

    refresh_response = client.refresh_access_token(
        client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
    )
    # logger.info(f"refresh_response: {refresh_response}")
    client.access_token = refresh_response["access_token"]

    return client


def upload_fit_to_strava(client, file_name, activity_name=None):
    with open(file_name, "rb") as f:
        r = client.upload_activity(
            activity_file=f, data_type="fit", name=activity_name)
        logger.info("uploaded: %s", file_name)


def upload_gpx_to_strava(client, file_name, activity_name=None):
    with open(file_name, "rb") as f:
        r = client.upload_activity(
            activity_file=f, data_type="gpx", name=activity_name)
        logger.info("uploaded: %s", file_name)


def test_run_strava_sync(client_id, client_secret, refresh_token):
    client = make_strava_client(client_id, client_secret, refresh_token)
    upload_fit_to_strava(client, "./activities/191842160_ACTIVITY.fit")


def sync_garmin_to_strava_all(strava_client, garmin_client):
    downloaded_activity_ids = [
        i.split("_")[0] for i in os.listdir("activities") if not i.startswith(".")
    ]

    uploaded = get_uploaded_activity_ids()
    logger.info(f"downloaded_activity_ids: {len(downloaded_activity_ids)}")
    new_activity_ids = list(
        set(downloaded_activity_ids) - set(uploaded))
    new_activity_ids.sort(key=int)

    logger.info(
        f"{len(new_activity_ids)} new activities to be upload to strava")

    try:
        for id in new_activity_ids[:50]:
            data = garmin_client.get_activity_evaluation(id)
            activityName = data['activityName']
            # logger.info(f"Got activity name: {activityName}")
            file_name = f"./activities/{id}_ACTIVITY.fit"

            if os.path.exists(file_name):
                logger.info(f"Uploading {file_name}: {activityName}")
                upload_fit_to_strava(strava_client, file_name, activityName)
                uploaded.append(id)
                time.sleep(1)
            else:
                file_name = f"./activities/{id}_ACTIVITY.gpx"
                logger.info(f"Uploading {file_name}: {activityName}")
                upload_gpx_to_strava(strava_client, file_name, activityName)
                uploaded.append(id)
                time.sleep(1)

    finally:
        set_uploaded_activity_ids(uploaded)


def sync_gpx_to_strava_all(strava_client, garmin_client):
    downloaded_activity_ids = [
        i.split(".")[0] for i in os.listdir("nrc_type_gpx_data") if not i.startswith(".")
    ]

    uploaded = get_uploaded_activity_ids()
    logger.info(f"downloaded_activity_ids: {len(downloaded_activity_ids)}")
    new_activity_ids = list(
        set(downloaded_activity_ids) - set(uploaded))
    new_activity_ids.sort(key=int)

    logger.info(
        f"{len(new_activity_ids)} new activities to be upload to strava")

    try:
        for id in new_activity_ids[:50]:
            file_name = f"./nrc_type_gpx_data/{id}.gpx"

            if os.path.exists(file_name):
                logger.info(f"Uploading {file_name}: {file_name}")
                upload_gpx_to_strava(strava_client, file_name)
                uploaded.append(id)
                time.sleep(1)

    finally:
        set_uploaded_activity_ids(uploaded)


def get_strava_activity_ids(client):
    activities = client.get_activities(limit=10)
    ids = []
    for activity in activities:
        ids.append(activity.id)
    # return ids + get_strava_activity_ids(client, limit=limit)
    return ids


def delete_strava_activities(client, activity_ids):
    for id in activity_ids:
        client.delete_activity(id)
        logger.info(f"Deleted activity {id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("strava_client_id", help="strava client id")
    parser.add_argument("strava_client_secret", help="strava client secret")
    parser.add_argument("strava_refresh_token", help="strava refresh token")
    parser.add_argument("garmin_email", nargs="?", help="email of garmin")
    parser.add_argument("garmin_password", nargs="?",
                        help="password of garmin")

    options = parser.parse_args()
    # run_strava_sync(options.strava_client_id, options.strava_client_secret,
    #                 options.strava_refresh_token)

    # strava_client
    strava_client = make_strava_client(
        options.strava_client_id,
        options.strava_client_secret,
        options.strava_refresh_token)

    # garmin_cn_client
    garmin_client = make_garmin_client(
        options.garmin_email,
        options.garmin_password)

    sync_garmin_to_strava_all(strava_client, garmin_client)
