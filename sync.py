import argparse
import datetime

import logging
import os

from garmin import download_activities_by_date, make_garmin_client
from strava import make_strava_client, upload_fit_to_strava
from utils import get_uploaded_activity_ids, set_uploaded_activity_ids

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# download all activities
# upload all activities to strava manually
# download today's activities
# auto upload today's activities to strava by github action


def sync_garmin_to_strava_all(strava_client, garmin_client):
    downloaded_activity_ids = [
        i.split("_")[0] for i in os.listdir("activities") if not i.startswith("_")
    ]
    logger.info(f"{downloaded_activity_ids}")
    for id in downloaded_activity_ids:
        data = garmin_client.get_activity_evaluation(id)
        activityName = data['activityName']
        # logger.info(f"Got activity name: {activityName}")
        file_name = f"./activities/{id}_ACTIVITY.fit"
        logger.info(f"Uploading {file_name}: {activityName}")
        upload_fit_to_strava(strava_client, file_name, activityName)


def sync_garmin_to_strava_difference(strava_client, garmin_client):
    downloaded_activity_ids = [
        i.split("_")[0] for i in os.listdir("activities") if not i.startswith("_")
    ]
    uploaded_activity_ids = get_uploaded_activity_ids()

    new_activity_ids = list(
        set(downloaded_activity_ids) - set(uploaded_activity_ids))

    logger.info(
        f"{len(new_activity_ids)} new activities to be upload to strava")

    try:
        for id in new_activity_ids:
            data = garmin_client.get_activity_evaluation(id)
            activityName = data['activityName']
            # logger.info(f"Got activity name: {activityName}")
            file_name = f"./activities/{id}_ACTIVITY.fit"
            logger.info(f"Uploading {file_name}: {activityName}")
            upload_fit_to_strava(strava_client, file_name, activityName)
            uploaded_activity_ids.append(id)
    finally:
        set_uploaded_activity_ids(uploaded_activity_ids)


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

    today = datetime.date.today()
    delta_days = datetime.timedelta(days=3)
    start_date = today - delta_days

    download_activities_by_date(garmin_client, start_date, today)
    sync_garmin_to_strava_difference(strava_client, garmin_client)
    # sync_garmin_to_strava_all(strava_client, garmin_client)
    # update_activity_status()
    # get_uploaded_activity_ids()
