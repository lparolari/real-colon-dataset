from downloader.api import get_files
from downloader.model import File
from typing import List, Optional
from tqdm import tqdm
import argparse
import re
import requests
import os
import hashlib
import logging


def mb(size: int):
    return size / 1024 / 1024


def filter_files(files: List[File], regex: str):
    if regex:
        files = [file for file in files if re.search(regex, file.name)]
    return files


def sort_files(files: List[File]):
    return sorted(files, key=lambda file: file.name)


def show_files(files: List[File]):
    print("File list:")
    for file in files:
        print(f"  {file.name} ({mb(file.size):.2f} MB)")


def download_file(file: File, output_dir: str = "."):
    download_url = file.download_url
    filename = file.name
    original_md5 = file.computed_md5

    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath):
        current_md5 = hashlib.md5(open(filepath, "rb").read()).hexdigest()
        if current_md5 == original_md5:
            logging.info(f"File {filename} already exists and has the correct md5")
            return

    r = requests.get(download_url, stream=True)
    with open(filepath, "wb") as f:
        for chunk in tqdm(
            r.iter_content(chunk_size=1024), desc=filename, unit="KB", leave=False
        ):
            if chunk:
                f.write(chunk)


def download_files(files: List[File], output_dir: Optional[str]):
    if not output_dir:
        logging.warning("No output directory specified, using current directory")
        output_dir = "."
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in tqdm(files):
        download_file(file, output_dir)


def print_help_filter():
    print("Examples:")
    print(
        """
> downloader --filter '001-001_(.*)'
001-001_annotations.tar.gz
001-001_frames.tar.gz
              
> downloader --filter '001-(.*)'
001-001_annotations.tar.gz
001-001_frames.tar.gz
001-002_annotations.tar.gz
001-002_frames.tar.gz
...
001-015_annotations.tar.gz
001-015_frames.tar.gz
            
> downloader --filter '001-(.*)_annotations(.*)'
001-001_annotations.tar.gz
001-002_annotations.tar.gz
001-003_annotations.tar.gz
...
001-015_annotations.tar.gz"""
    )


def ask_confirmation(skip=False):
    if skip:
        return

    print("Do you want to continue with the download? [Y/n]", end=" ")
    answer = input() or "Y"

    if answer.lower() != "y":
        exit()


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Download the files included in REAL-Colon dataset."
    )
    parser.add_argument(
        "--help-filter", help="Show help for filtering feature", action="store_true"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="Regex to filter files by name (see `--help-filter`)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show more information (e.g. file list)",
        action="store_true",
    )
    parser.add_argument(
        "-y",
        "--yes",
        help="Do not ask for confirmation",
        action="store_true",
    )

    article_id = "22202866"  # article id for realcolon dataset

    args = parser.parse_args()

    if args.help_filter:
        print_help_filter()
        return

    files = get_files(article_id)
    files = filter_files(files, args.filter)
    files = sort_files(files)

    if args.verbose:
        show_files(files)

    n_files = len(files)
    tot_size = sum([file.size for file in files])

    print(f"Found {n_files} files (total size {mb(tot_size):.2f} MB)")

    ask_confirmation(skip=args.yes)

    download_files(files, args.output_dir)


if __name__ == "__main__":
    main()
