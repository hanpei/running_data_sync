import argparse
import datetime
import json

import logging
import os
import sys

from garmin import download_activities_by_date, make_garmin_client
from strava import make_strava_client, sync_garmin_to_strava_all, upload_fit_to_strava
from utils import get_uploaded_activity_ids, set_uploaded_activity_ids

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# download all activities
# upload all activities to strava manually
# download today's activities
# auto upload today's activities to strava by github action


# 同步近三天数据
def sync_last_three_days():
    today = datetime.date.today()
    delta_days = datetime.timedelta(days=3)
    start_date = today - delta_days

    download_activities_by_date(garmin_client, start_date, today)
    sync_garmin_to_strava_all(strava_client, garmin_client)


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

    # get last upload id
    upload_ids = get_uploaded_activity_ids()
    last_upload_id = upload_ids[-1] if len(upload_ids) > 0 else None
    if last_upload_id is None:
        sys.exit(1)

    activity = garmin_client.get_activity_evaluation(last_upload_id)
    start_time = activity.get('summaryDTO').get('startTimeLocal')
    start_date = datetime.datetime.fromisoformat(
        start_time.split(".")[0]).date()
    logger.info(f"last upload id: {last_upload_id}, date: {start_date}")

    download_activities_by_date(
        garmin_client, start_date, datetime.date.today())
    sync_garmin_to_strava_all(strava_client, garmin_client)
