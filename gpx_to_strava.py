import argparse
import json
import logging
import os
import time
from stravalib.client import Client
from stravalib.util.limiter import RateLimiter, XRateLimitRule
from garmin import make_garmin_client
from strava import make_strava_client, upload_gpx_to_strava
from utils import get_uploaded_activity_ids, get_uploaded_nrc_timestamps, set_uploaded_activity_ids, set_uploaded_nrc_timestamps

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_gpx_to_strava_all(strava_client):
    downloaded_activity_ids = [
        i.split(".")[0] for i in os.listdir("nrc_type_gpx_data") if not i.startswith(".")
    ]

    uploaded = get_uploaded_nrc_timestamps()
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
        set_uploaded_nrc_timestamps(uploaded)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("strava_client_id", help="strava client id")
    parser.add_argument("strava_client_secret", help="strava client secret")
    parser.add_argument("strava_refresh_token", help="strava refresh token")

    options = parser.parse_args()
    # run_strava_sync(options.strava_client_id, options.strava_client_secret,
    #                 options.strava_refresh_token)

    # strava_client
    strava_client = make_strava_client(
        options.strava_client_id,
        options.strava_client_secret,
        options.strava_refresh_token)

    sync_gpx_to_strava_all(strava_client)
