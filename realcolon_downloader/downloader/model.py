from typing import List

from pydantic import BaseModel


class APIError(Exception):
    pass


class File(BaseModel):
    id: int
    name: str
    size: int
    is_link_only: bool
    download_url: str
    supplied_md5: str
    computed_md5: str
    mimetype: str
