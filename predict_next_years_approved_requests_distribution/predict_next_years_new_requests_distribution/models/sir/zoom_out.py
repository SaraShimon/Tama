#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import json
from geopy.geocoders import Nominatim


tama_df = pd.read_csv('engineered_tama_data.csv')

def get_city_coordinates(city):
    # Create a geocoder instance
    geolocator = Nominatim(user_agent="my_app")
    # Geocode the city to get the location information
    location = geolocator.geocode(city, language="he", timeout=10)
    # Extract the latitude and longitude from the location data
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return longitude, latitude
    return None, None


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers

    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the differences in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Apply the Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


def get_nearest_city(longitude, latitude, existing_cities, tama_df):
    tama_df = tama_df[tama_df['city_code'].isin(existing_cities)]
    # Calculate the distance from the reference point for each row in the dataframe
    tama_df['distance'] = tama_df.apply(lambda row: calculate_distance(latitude, longitude, row['latitude'], row['longitude']), axis=1)

    # Find the row with the minimum distance
    nearest_point = tama_df.loc[tama_df['distance'].idxmin()]

    # Print the nearest point
    nearest_city = nearest_point['hebrew_city_name']
    print('nearest city', nearest_city)
    return nearest_city


def zoom_out(city, tama_df):
    with open("sir_model.json") as sir_nodel_file:
        sir_models = json.load(sir_nodel_file)
        existing_cities = [model['city'] for model in sir_models]
    if city not in existing_cities:
        print('zoom out')
        city_df = tama_df[tama_df['hebrew_city_name'] == city]
        if city_df.empty:
            longitude, latitude = get_city_coordinates(city)
        else:
            longitude, latitude = city_df['longitude'].iloc[0], city_df['latitude'].iloc[0]
        return get_nearest_city(longitude, latitude, existing_cities, tama_df)
    return city


def get_city_code(city, tama_df):
    city_map_name_to_code = tama_df[['hebrew_city_name', 'city_code']].drop_duplicates()
    city_map_name_to_code = city_map_name_to_code[city_map_name_to_code['hebrew_city_name'] == city]['city_code']
    return int(city_map_name_to_code)


def get_city_name(city, tama_df):
    city_map_name_to_code = tama_df[['hebrew_city_name', 'city_code']].drop_duplicates()
    city_map_name_to_code = city_map_name_to_code.loc[city_map_name_to_code['city_code'] == city, 'hebrew_city_name']
    return list(city_map_name_to_code.values)[0]
