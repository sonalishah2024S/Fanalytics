import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

df = pd.read_csv("power4_attributes(Sheet1).csv")

geolocator = Nominatim(user_agent="power4_geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

df = pd.read_csv("power4_attributes(Sheet1).csv")

cache = {}

def get_lat_lon(city):
    if pd.isna(city) or city == "":
        return None, None
    if city in cache:
        return cache[city]

    location = geocode(city)
    if location:
        result = (location.latitude, location.longitude)
    else:
        result = (None, None)

    cache[city] = result
    return result

for col in ["City 1", "City 2", "City 3"]:
    df[[f"{col}_lat", f"{col}_lon"]] = df[col].apply(
        lambda x: pd.Series(get_lat_lon(x))
    )

df.to_csv("geocoded_power4.csv", index=False)

print("Done! Saved as geocoded_power4.csv")