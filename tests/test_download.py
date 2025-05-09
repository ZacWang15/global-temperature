from global_temperature.tools.download import (
    download_file,
    extract_file,
    delete_file,
    download,
)
from pathlib import Path
import shutil
import pytest


def test_download_functions():
    """Test the download functions"""
    data_type = "monthly"
    year = 2024

    target_folder = "tests/data"
    local_path = Path(target_folder) / f"{data_type}" / f"year={year}.tar.xz"
    url = f"https://global-temperature.com/{data_type}/year={year}.tar.xz"

    # Test downloading a file
    download_file(local_path, url)

    # Check if the file exists
    assert local_path.exists(), f"File {local_path} was not downloaded."

    # Extract file
    extract_file(local_path)
    # Check if the extraction was successful
    extract_path = local_path.parent / str(local_path.name).split(".")[0]
    assert extract_path.exists(), f"Extraction failed for {local_path}."

    # Delete tar.xz file
    delete_file(local_path)
    # Check if the file was deleted
    assert not local_path.exists(), f"File {local_path} was not deleted."

    # Clean up
    shutil.rmtree(target_folder, ignore_errors=True)


def test_download_invalid_paramters():
    """Test the download function with invalid parameters"""
    target_folder = "tests/data"

    with pytest.raises(ValueError):
        download(target_path=target_folder)


@pytest.mark.parametrize(
    "years",
    [[2050], ["2050"], [1940]],
)
def test_download_invalid_years(years):
    """Test the download function with invalid parameters"""
    target_folder = "tests/data"

    with pytest.raises(ValueError):
        download(
            target_path=target_folder,
            years=years,
        )


def test_download():
    """Test the download function"""
    data_type = "monthly"
    years = [2000, 2021]
    target_folder = "tests/data"

    # Test downloading a file
    failed_years = download(
        target_path=target_folder,
        years=years,
        data_type=data_type,
        max_tries=2,
        delete_archived_files=True,
    )

    # Check if the file exists
    assert not failed_years, f"Download failed for the following years: {failed_years}"

    # Check if the files were downloaded
    for year in years:
        # .tar.xz files are supposed to be deleted when delete_archived_files is True
        local_path = Path(target_folder) / f"{data_type}" / f"year={year}.tar.xz"
        assert not local_path.exists(), f"File {local_path} was not downloaded."

        # Check if the extraction was successful
        extract_path = local_path.parent / str(local_path.name).split(".")[0]
        assert extract_path.exists(), f"Extraction failed for {local_path}."

    # Clean up
    shutil.rmtree(target_folder, ignore_errors=True)
