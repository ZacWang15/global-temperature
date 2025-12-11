from pathlib import Path
import requests
from typing import List, Union
import tarfile
from .validate import check_year
from ..config import load_config
from urllib.parse import urljoin
import logging
from datetime import datetime


CONFIG = load_config()
logger = logging.getLogger(__name__)


def download(
    target_path: str | Path,
    years: Union[List[int], None] = None,
    start_year: Union[int, None] = None,
    end_year: Union[int, None] = None,
    max_tries: int = 2,
    data_type: str = "monthly",
    delete_archived_files: bool = True,
    overwrite: bool = False,
) -> List[int]:
    """
    Downloads data from Cloudflare R2 for the specified years or range of years.

    Args:
        target_path (str): The directory where the data will be downloaded.
        years (List[int], optional): A list of specific years to download.
        start_year (int, optional): The start year for the range of years to download.
        end_year (int, optional): The end year for the range of years to download.
        max_tries (int, optional): The maximum number of download attempts. Defaults to 2.
        data_type (str): The type of data to download. Currently, only "monthly" is supported.
        delete_archived_files (bool): Whether to delete the archived files after extraction.
        overwrite (bool): Whether to overwrite existing files. e.g. If monthly/year=2021 folder exist, skip downloading this year. Defaults to False.

    Returns:
        List[int]: A list of years for which the download failed.

    Raises:
        ValueError: If neither `years` nor `start_year` and `end_year` are provided.
    """
    if data_type != "monthly":
        raise ValueError("Only 'monthly' data type is supported.")

    if years is None and (start_year is None or end_year is None):
        raise ValueError(
            "You must provide either a list of years or a start and end year."
        )

    if years is None:
        years = list(range(start_year, end_year + 1))

    # Validate the year
    [check_year(year) for year in years]

    target_path = Path(target_path) / f"{data_type}"
    target_path.mkdir(parents=True, exist_ok=True)

    failed_years = []

    for year in years:
        # Form download URL
        base_url = CONFIG["base_url"]
        path_template = f"{data_type}/year={year}.tar.xz"
        url = urljoin(base_url, path_template)

        file_name = f"year={year}.tar.xz"
        file_path = target_path / file_name

        # Check if the year={year} folder already exists. For current year, we must overwrite it in case there is a new monthly data.
        if (
            overwrite is False
            and (target_path / f"year={year}").is_dir()
            and year != datetime.now().year
        ):
            logger.info(f"Skipping download for {year}. Folder already exists.")
            continue

        success = False
        retries = 0
        while retries < max_tries and not success:
            success = download_file(file_path, url)
            if success:
                break
            else:
                logger.info(f"Failed to download {url}. Retrying...")
                retries += 1

        if not success:
            logger.info(f"Failed to download {url} after {max_tries} attempts.")
            failed_years.append(year)

        # Extract the file if download was successful
        if success:
            extract_file(file_path)
            if delete_archived_files:
                delete_file(file_path)

    if failed_years:
        logger.info(
            f"Download failed for the following years after 2 retries: {failed_years}"
        )

    return failed_years


def download_file(target_file: Path, url: str) -> bool:
    """
    Downloads a file from the specified URL.

    Args:
        target_file (Path): The path to the file to download.
        url (str): The URL to download the file from.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    logger.info(f"Downloading {url}")
    response = requests.get(url, stream=True)

    # Ensure the target directory exists
    target_file.parent.mkdir(parents=True, exist_ok=True)

    if response.status_code == 200:
        with target_file.open("wb") as file:
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                logger.info(f"Downloaded {target_file.name} to {target_file}")
                return True
            except Exception as e:
                logger.error(
                    f"Error during download or writing file {target_file.name}: {e}"
                )
                return False


def extract_file(file_path: str | Path):
    """
    Extracts a .tar.xz file to the same folder as the file's parent folder.

    Args:
        file_path (str | Path): The path to the .tar.xz file to extract.
    """
    file_path = Path(file_path)

    if not file_path.is_file() or not file_path.suffixes == [".tar", ".xz"]:
        logger.error(f"Invalid file: {file_path}. Must be a .tar.xz file.")
        return

    extract_path = file_path.parent / str(file_path.name).split(".")[0]

    try:
        logger.info(f"Extracting {file_path} to {extract_path}")
        with tarfile.open(file_path, "r:xz") as tar:
            tar.extractall(path=extract_path)
            logger.info(f"Extracted {file_path} to {extract_path}")
    except Exception as e:
        logger.error(f"Failed to extract {file_path}: {e}")


def delete_file(file_path: str | Path):
    """
    Deletes the specified file.

    Args:
        file_path (str): The path to the file to delete.
    """
    file_path = Path(file_path)

    if file_path.is_file():
        try:
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
    else:
        logger.info(f"Path {file_path} does not exist or is not a file.")
