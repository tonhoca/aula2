# -*- coding: utf-8 -*-
"""
General purpose tasks for dumping data from URLs.
"""
from datetime import timedelta
import io
from pathlib import Path
from urllib.error import HTTPError

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from prefect import task
import requests

from pipelines.constants import constants
from pipelines.utils.utils import get_credentials_from_env, log


@task(
    checkpoint=False,
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def download_url(url: str, fname: str, gdrive_url: bool = False) -> None:
    """
    Downloads a file from a URL and saves it to a local file.
    Try to do it without using lots of RAM.

    Args:
        url: URL to download from.
        fname: Name of the file to save to.

    Returns:
        None.
    """
    if not gdrive_url:
        log(">>>>> URL is not a Google Drive URL, downloading directly")
        filepath = Path(fname)
        filepath.mkdir(parents=True, exist_ok=True)
        req = requests.get(url, stream=True)
        with open(fname, "wb") as file:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    file.flush()
    else:
        log(">>>>> URL is a Google Drive URL, downloading from Google Drive")
        # URL is in format
        # https://drive.google.com/file/d/<FILE_ID>/...
        # We want to extract the FILE_ID
        log(">>>>> Extracting FILE_ID from URL")
        url_prefix = "https://drive.google.com/file/d/"
        if not url.startswith(url_prefix):
            raise ValueError(
                "URL must start with https://drive.google.com/file/d/."
                f"Invalid URL: {url}"
            )
        file_id = url.removeprefix(url_prefix).split("/")[0]
        log(f">>>>> FILE_ID: {file_id}")
        creds = get_credentials_from_env(
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        try:
            service = build("drive", "v3", credentials=creds)
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(fname, mode="wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                log(f"Downloading file... {int(status.progress() * 100)}%.")
        except HTTPError as error:
            log(f"HTTPError: {error}", "error")
            raise error
