from global_temperature.tools.download import download

# The available range of years is from 1990 to 2025
start_year = 2023
end_year = 2024
target_path = "examples/data"

# the function will download the data from the API and returnes the years that failed to download
# failed_years = download(
#     start_year=start_year,
#     end_year=end_year,
#     target_path=target_path,
#     # delete_archived_files=False,  # if you want to keep the zipped files
# )

# Or can you specify the years that you want to download
years = [2021, 2022, 2023, 2025]
# failed_years = download(years=years, target_path=target_path)

# 2. After downloading the file, you can query any locations
import global_temperature as gt

temperature_monthly = gt.TemperatureFactory.create_temperature_object(
    data_type="monthly",
    # specify the folder that you downloaded the data (if possible, use abosolute path)
    source_folder=target_path,
)

# Query the temperature for a specific year, month, latitude, and longitude
year = 2025
month = 4
latitude = -37.81855964
longitude = 144.99806817
temp = temperature_monthly.query(year, month, latitude, longitude)
print(
    f"Temperature in {year}-{month} at ({latitude}, {longitude}): {temp['temperature']} °C"
)
print(temp)
