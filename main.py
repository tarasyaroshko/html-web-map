"""
Module which creates
HTML web map
"""
import argparse
from tabnanny import check
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from haversine import haversine
pd.options.mode.chained_assignment = None

def calculate_haversine_distance(place1, place2):
    """
    Calculates distance between two points
    using haversine module.

    Args:
        place1 (Tuple[float, float]): coordinates of first point
        place2 (Tuple[float, float]): coordinates of second point

    Returns:
        distance (float): distance between place1 and place2
    """
    distance = haversine(place1, place2)
    return distance

def read_file(filename):
    """
    Reads info from the file, then returns
    a DataFrame with all essential info.

    Args:
        filename (str): path to file with films
    Returns:
        pd.DataFrame: pandas DataFrame with columns
        "Movie", "Year", "Location"
    """
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()[14:]
        list_of_rows = []
    for line in lines:
        line = line.strip().split("\t")
        movie = line[0].rsplit("{", 1)[0].rsplit("(")[0].rstrip(" ")
        year = line[0].rsplit("{", 1)[0].rsplit("(")[1].strip(" )")
        if line[-1].endswith(')'):
            location = line[-2]
        else:
            location = line[-1]
        list_of_rows.append([movie, year, location])
    df = pd.DataFrame(list_of_rows, columns=['Movie', 'Year', 'Location'])
    return df

def find_coordinates(location_address):
    """
    Returns coordinates of a certain address.

    Args:
        location_address (str): the address of desired location
    
    Returns:
        Tuple[float, float]: latitude and longtitude floats of location
    """
    geolocator = Nominatim(user_agent="misc-request")
    try:
        location = geolocator.geocode(location_address)
        if location is None:
            raise GeocoderUnavailable
    except GeocoderUnavailable:
        return find_coordinates(", ".join(location_address.split(", ")[1:]))
    return location.latitude, location.longitude


def find_closest_films_in_df(df, year, location):
    """
    Returns DataFrame with 7 or less films that
    are closest to the desired location

    Args:
        films (pd.DataFrame): df with all needed info
        location (Tuple[float, float]): the given location
        year (str): year to search with

    Returns:
        pd.DataFrame: closest 7 or less films
    """
    desired_year_films = df.loc[df['Year'] == year]
    movie_list = desired_year_films['Movie'].tolist()
    locations_list = desired_year_films['Location'].tolist()
    coordinates_list = []
    movie_and_year_list = list(zip(movie_list, locations_list))
    for index, element in enumerate(locations_list):
        coordinates_list.append(find_coordinates(element))
    desired_year_films['Coordinates'] = coordinates_list
    distance_list = []
    for index, element in enumerate(coordinates_list):
        distance_list.append(calculate_haversine_distance(location, element))
    desired_year_films['Distance'] = distance_list
    desired_year_films['Movie and Year'] = movie_and_year_list
    desired_year_films = desired_year_films.drop_duplicates(subset=['Movie and Year'], keep='first')
    desired_year_films = desired_year_films.drop("Movie and Year", axis=1)
    desired_year_films.sort_values(by="Distance", ascending=True, inplace=True)
    desired_year_films.reset_index(drop=True, inplace=True)
    if len(desired_year_films) > 7:
        desired_year_films = desired_year_films[:8]
    return desired_year_films

def check_for_multiple_films(df: pd.DataFrame) -> dict:
    """
    Returns dictionary with all films
    on a certain location.
    Args:
        df (pd.DataFrame): df with all info about films
    Returns:
        films_on_location_dict (dict): dict with all films 
        on a certain location
    """
    films_on_location_dict = dict()
    for i in range(len(df)):
        if df.iloc[i]["Coordinates"] not in films_on_location_dict.keys():
            films_on_location_dict[df.iloc[i]["Coordinates"]] = [
                (df.iloc[i]["Movie"])
            ]
        else:
            films_on_location_dict[df.iloc[i]["Coordinates"]].append(
                (df.iloc[i]["Movie"])
            )
    return films_on_location_dict


def inception_film_locations(df):
    """
    Returns a DataFrame with all the 
    locations which were used when
    shooting "Inception" movie
    
    Args:
        path (str): path to file with films
        location (Tuple[float, float]): latitude and longtitude of your location
        year (int): year to search for
    
    Returns:
        inception_film_locations (pd.DataFrame): df with all info about
        the locations
    """
    inception_locations = df.loc[df['Movie'] == "Inception"]
    inception_locations = inception_locations.loc[inception_locations['Year'] == '2010']
    if "Coordinates" not in inception_locations.columns:
        inception_locations["Coordinates"] = inception_locations["Location"].apply(find_coordinates)
    inception_locations.reset_index(inplace=True, drop=True)
    return inception_locations

def create_map(filename,location,year):
    """
    Creates a web map and then saves 
    it to Map.html

    Args:
        path (str): path to file with films
        location (Tuple[float, float]): latitude and longtitude of your location
        year (int): year to search for
    """
    map = folium.Map(location=location, zoom_start=4)
    df = read_file(filename)
    closest_films = find_closest_films_in_df(df, str(year), location)
    closest_films_layer = folium.FeatureGroup(name=f"Closest Films Made In {year}")
    inception_locations = inception_film_locations(df)
    inceptions_locations_layer = folium.FeatureGroup(name = f"Inception Movie Locations")
    locations = check_for_multiple_films(closest_films)
    for coordinates in locations.keys():
        closest_films_layer.add_child(folium.Marker(location=coordinates, popup=locations[coordinates],icon=folium.Icon(color='orange', fill=True,fill_color='orange')))
    for i in range(len(inception_locations)):
        located = inception_locations.iloc[i]["Coordinates"]
        name = inception_locations.iloc[i]["Location"]
        inceptions_locations_layer.add_child(folium.Marker(location=located, popup=name,icon=folium.Icon(color='purple', fill=True,
                                                            fill_color='purple')))
    current_location = folium.CircleMarker(
        location=location,
        radius=15,
        popup="Your Location",
        fill_color="red",
        color="red",
        fill_opacity=0.5,
    )
    map.add_child(current_location)
    map.add_child(closest_films_layer)
    map.add_child(inceptions_locations_layer)
    map.add_child(folium.LayerControl())
    map.save("Map.html")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int)
    parser.add_argument('latitude', type=float)
    parser.add_argument('longitude', type=float)
    parser.add_argument('path_to_dataset', type=str)
    args = parser.parse_args()
    parser = argparse.ArgumentParser()
    create_map(args.path_to_dataset,(args.latitude, args.longitude),args.year)