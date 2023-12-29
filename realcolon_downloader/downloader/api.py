from typing import List

import requests
from downloader.model import APIError, File


base_url = lambda: "https://api.figshare.com/v2"


def get_files(article_id: str) -> List[File]:
    """
    Get a list of files for the REAL-Colon dataset.
    """
    url = f"{base_url()}/articles/{article_id}/files"

    # https://docs.figshare.com/#article_files
    response = requests.get(url)

    if not response.ok:
        raise APIError(response.json())

    files = response.json()
    files = [File(**file) for file in files]
    return files
