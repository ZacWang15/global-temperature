from pathlib import Path
import requests
from typing import List, Union
import tarfile


def download_data(
    target_path: str,
    years: Union[List[int], None] = None,
    start_year: Union[int, None] = None,
    end_year: Union[int, None] = None,
):
    """
    Downloads data from Cloudflare R2 for the specified years or range of years.

    Args:
        target_path (str): The directory where the data will be downloaded.
        years (List[int], optional): A list of specific years to download.
        start_year (int, optional): The start year for the range of years to download.
        end_year (int, optional): The end year for the range of years to download.

    Raises:
        ValueError: If neither `years` nor `start_year` and `end_year` are provided.
    """
    target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)

    if years is None and (start_year is None or end_year is None):
        raise ValueError(
            "You must provide either a list of years or a start and end year."
        )

    if years is None:
        years = list(range(start_year, end_year + 1))

    base_url = "https://global-temperature.com/monthly/{year}=1990.tar.xz"

    for year in years:
        url = base_url.format(year=year)
        file_name = f"{year}=1990.tar.xz"
        file_path = target_path / file_name

        print(f"Downloading {url}...")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with file_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded {file_name} to {target_path}")
        else:
            print(f"Failed to download {url}. HTTP Status Code: {response.status_code}")


# Example usage:
# download_data(target_path="./data", start_year=1990, end_year=1995)
# download_data(target_path="./data", years=[1990, 1991, 1992])


def extract_and_cleanup(target_path: str, years: List[int]):
    """
    Extracts tar.xz files and deletes the original files.

    Args:
        target_path (str): The directory where the tar.xz files are located.
        years (List[int]): A list of years corresponding to the files to extract.
    """
    target_path = Path(target_path)

    for year in years:
        file_name = f"{year}=1990.tar.xz"
        file_path = target_path / file_name
        extract_path = target_path / f"{year}=1990"

        if file_path.exists():
            print(f"Extracting {file_name}...")
            try:
                with tarfile.open(file_path, "r:xz") as tar:
                    tar.extractall(path=extract_path)
                print(f"Extracted {file_name} to {extract_path}")
                file_path.unlink()  # Delete the file
                print(f"Deleted {file_name}")
            except Exception as e:
                print(f"Failed to extract {file_name}: {e}")
        else:
            print(f"File {file_name} does not exist.")
