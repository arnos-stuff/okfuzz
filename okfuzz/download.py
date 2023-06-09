"""
A rudimentary URL downloader (like wget or curl) to demonstrate Rich progress bars.
"""

import os.path
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import signal
import shutil
from functools import partial
from threading import Event
from typing import Iterable
from urllib.request import urlopen

__all__ = ["download", "copy_url", "progress"]

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


def copy_url(task_id: TaskID, url: str, path: str) -> None:
    """Copy data from a url to a local file."""
    progress.console.log(f"Requesting {url}")
    response = urlopen(url)
    # This will break if the response doesn't contain content length
    progress.update(task_id, total=int(response.info()["Content-length"]))
    with open(path, "wb") as dest_file:
        progress.start_task(task_id)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            progress.update(task_id, advance=len(data))
            if done_event.is_set():
                return
    progress.console.log(f"Downloaded {path}")


def download(urls: Iterable[str], dest_dir: str):
    """Download multiple files to the given directory."""

    with progress:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for url in urls:
                filename = url.split("/")[-1]
                dest_path = os.path.join(dest_dir, filename)
                task_id = progress.add_task("download", filename=filename, start=False)
                pool.submit(copy_url, task_id, url, dest_path)
                
        final_task = progress.add_task("Unzipping...", filename="Unzipping...", start=False)
        
        dest = Path(dest_dir)
        
        for f in dest.iterdir():
            if f.is_file() and f.suffix in [".zip", ".gz", ".tar", ".tar.gz", ".tar.bz2", ".bz2"]:
                progress.update(final_task, filename=f.name)
                shutil.unpack_archive(f, dest_dir)
                f.unlink()


if __name__ == "__main__":
    # Try with https://releases.ubuntu.com/20.04/ubuntu-20.04.3-desktop-amd64.iso
    if sys.argv[1:]:
        download(sys.argv[1:], "./")
    else:
        print("Usage:\n\tpython downloader.py URL1 URL2 URL3 (etc)")