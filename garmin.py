#!/usr/bin/env python3
import argparse
import asyncio
import os
import time
import sys

import logging
import datetime
import zipfile
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

from numpy import void

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_garmin_client(email, password, is_cn=True):
    client = Garmin(email, password, is_cn)
    # Login to Garmin Connect portal
    success = client.login()
    if not success:
        print("Login failed")
        sys.exit(1)

    # Get full name from profile
    logger.info(client.get_full_name())
    return client

# download activities from a specific date


def download_activities_by_date(client, start_date: str, end_date: str):
    # make dir
    os.makedirs("activities", exist_ok=True)
    os.makedirs("download", exist_ok=True)

    activities = client.get_activities_by_date(start_date, end_date)

    for activity in activities:
        activity_id = activity["activityId"]

        logger.info("api.download_activities(%s)", activity_id)

        zip_data = client.download_activity(
            activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL)
        output_file = f"./download/{str(activity_id)}.zip"
        with open(output_file, "wb") as fb:
            fb.write(zip_data)

        zip_file = open(output_file, 'rb')
        z = zipfile.ZipFile(zip_file)
        for name in z.namelist():
            z.extract(name, "./activities")
        zip_file.close()


# Download all activities
async def download_activites_by_id(client, activity_id):

    logger.info("api.download_activities(%s)", activity_id)

    zip_data = client.download_activity(
        activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL)
    output_file = f"./download/{str(activity_id)}.zip"
    with open(output_file, "wb") as fb:
        fb.write(zip_data)

    zip_file = open(output_file, 'rb')
    z = zipfile.ZipFile(zip_file)
    for name in z.namelist():
        z.extract(name, "./activities")
    zip_file.close()


def get_activity_id_list(client, start=0):
    activities = client.get_activities(start, 100)
    if activities:
        ids = list(map(lambda a: str(a.get("activityId", "")), activities))
        print(f"Syncing Activity IDs")
        return ids + get_activity_id_list(client, start + 100)
    else:
        return []


def get_activity_last_100(client, start=0):
    activities = client.get_activities(0, 2)
    logger.info(f" activity  {str(activities)}")

    ids = list(map(lambda a: str(a.get("activityId", "")), activities))
    return ids


# Semaphore to limit the number of concurrent connections
async def gather_with_concurrency(n, tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email", nargs="?", help="email of garmin")
    parser.add_argument("password", nargs="?", help="password of garmin")

    parser.add_argument(
        "--all",
        dest="all",
        action="store_true",
        help="if download all activities",
    )
    options = parser.parse_args()
    email = options.email
    password = options.password
    donwload_all = options.all

    if email == None or password == None:
        print("Missing argument nor valid configuration file")
        sys.exit(1)

    # make dir
    os.makedirs("activities", exist_ok=True)
    os.makedirs("download", exist_ok=True)

    async def download_new_activities():
        # Initialize Garmin api with your credentials
        client = Garmin(email, password, True)
        # Login to Garmin Connect portal
        success = client.login()
        if not success:
            print("Login failed")
            sys.exit(1)

        # Get full name from profile
        logger.info(client.get_full_name())

        # because I don't find a para for after time, so I use garmin-id as filename
        # to find new run to generage
        downloaded_ids = [
            i.split(".")[0] for i in os.listdir("download") if not i.startswith(".")
        ]
        activity_ids = get_activity_id_list(client)

        to_generate_garmin_ids = list(set(activity_ids) - set(downloaded_ids))
        print(f"{len(to_generate_garmin_ids)} new activities to be downloaded")

        start_time = time.time()
        await gather_with_concurrency(
            10, [download_activites_by_id(client, id)
                 for id in to_generate_garmin_ids]
        )
        print(f"Download finished. Elapsed {time.time()-start_time} seconds")

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(download_new_activities())
    loop.run_until_complete(future)
