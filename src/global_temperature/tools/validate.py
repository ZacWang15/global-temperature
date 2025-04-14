import pandas as pd


def check_file(file_path: str, file_format: str = "parquet") -> bool:
    """
    Check if the file is a parquet file.
    """
    if not file_path.endswith(f".{file_format}"):
        raise ValueError(f"File is not a {file_format} file: {file_path}")

    return True


def check_df_columns(df: pd.DataFrame, columns: list[str]) -> bool:
    """
    Check if the DataFrame has the required columns.
    """
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in DataFrame: {missing_columns}")
    return True


def check_coordinates(latitude: float, longitude: float) -> bool:
    """
    Check if the coordinates are valid.
    """
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude {latitude} is out of bounds.")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude {longitude} is out of bounds.")
    return True


def check_year(year: int) -> bool:
    """
    Check if the year is valid.
    """
    if not (1950 <= year <= 2100):
        raise ValueError(f"Year {year} is out of bounds.")
    if not isinstance(year, int):
        raise ValueError(f"Year {year} is not an integer.")
    return True


def check_month(month: int) -> bool:
    """
    Check if the month is valid.
    """
    if not (1 <= month <= 12):
        raise ValueError(f"Month {month} is out of bounds.")
    if not isinstance(month, int):
        raise ValueError(f"Month {month} is not an integer.")
    return True


def check_day(day: int) -> bool:
    """
    Check if the day is valid.
    """
    if not (1 <= day <= 31):
        raise ValueError(f"Day {day} is out of bounds.")
    if not isinstance(day, int):
        raise ValueError(f"Day {day} is not an integer.")
    return True
