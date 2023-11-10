# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

# ----------------------------------
# NOTE: This code was originally written by Federico Tartarini (see https://github.com/FedericoTartarini/youtube-api-edit-videos-metadata).
# I updated it (with the help of ChatGPT, and it works, yay!) in order to be compliant with the 2.1.2 version of the pandas library.
# ----------------------------------

# This Python file, along with the rest of the repo, isn't protected by any kind of copyright. However, if you modify the code and publish it, we would like to see proper credit.

# Mar 7, 2021 - Federico Tartarini | https://github.com/FedericoTartarini

# Nov 11, 2023 - Giovanni Rota | https://github.com/Glort572

# =========================================================================

import os
import json
import mysecrets
import pandas as pd

import googleapiclient.discovery


def authenticate():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=mysecrets.developer_key  # Either make new file "mysecrets.py" or replace "mysecrets.developer_key" with the API key 
    )

    return youtube


def get_video_ids(channel_id):
    youtube = authenticate()

    more_than_50_results = True
    next_page_token = ""

    while more_than_50_results:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token,
            type="video",
        )

        response = request.execute()

        if "nextPageToken" in response.keys():
            next_page_token = response["nextPageToken"]
        else:
            more_than_50_results = False

        video_ids = [
            x["id"]["videoId"]
            for x in response["items"]
            if x["id"]["kind"] == "youtube#video"
        ]

        df_ids = pd.DataFrame(columns=["video-ids"])
        try:
            df_ids = pd.read_csv(file_video_ids)
        except FileNotFoundError:
            pass

        # Concatenate the existing DataFrame and the new video IDs, drop duplicates
        df_ids = pd.concat([df_ids, pd.DataFrame(video_ids, columns=["video-ids"])], ignore_index=True).drop_duplicates()

        # Save the updated DataFrame to the CSV file
        df_ids.to_csv(file_video_ids, index=False)


def get_video_description():
    youtube = authenticate()

    df_ids = pd.read_csv(file_video_ids)

    dict_videos = {}

    for video_id in df_ids["video-ids"].unique():
        try:
            request = youtube.videos().list(part="snippet", id=video_id)

            response = request.execute()

            if response.get("items") and len(response["items"]) > 0:
                snippet = response["items"][0]["snippet"]
                title = snippet.get("title", "")
                description = snippet.get("description", "").split("\n")
                tags = snippet.get("tags", [])

                dict_video = {
                    "title": title,
                    "description": description,
                    "tags": tags,
                }

                dict_videos[video_id] = dict_video
            else:
                print(f"Warning: No data found for video with ID {video_id}")

        except Exception as e:
            print(f"Error processing video with ID {video_id}: {e}")

    with open("video_info.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(dict_videos, indent=2))


if __name__ == "__main__":

    file_video_ids = "video_ids.csv"

    # download ids of all the videos in your channel
    get_video_ids(channel_id="UCRjhrVMfeAurqHm4BnTNgyw")

    # get info from the video you uploaded on your channel
    get_video_description()
