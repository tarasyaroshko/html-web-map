# import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
import folium, argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('year')
# parser.add_argument('latitude')
# parser.add_argument('longitude')
# parser.add_argument('path_to_dataset')
# args = parser.parse_args()
# year = args.year
# latitude = args.latitude
# longitude = args.longitude
# path_to_dataset = args.path_to_dataset



geolocator = Nominatim(user_agent="taras.yaroshko@ucu.edu.ua")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
location_address = geolocator.geocode("175 5th Avenue NYC")

# import pandas as pd
# read_file = pd.read_csv (r'locations.list', error_bad_lines=False, skiprows=13,delimiter= ' ')
# read_file.to_csv (r'locations.csv', index=None)
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from haversine import haversine, Unit



movies = []
years = []
locations = []
latitudes = []
longitudes = []
distances = []
filename = 'locations1.list'
with open(filename, 'r') as file:
    for line in file:
        line = line.strip().split("\t")
        lol = line[0].rsplit("{", 1)
        movie_and_year_split = lol[0].rsplit("(")
        movie = movie_and_year_split[0].rstrip(" ")
        year2 = movie_and_year_split[1].strip(" )")
        if year2 == '2015':
            movies.append(movie.strip())
            # years.append(year2)
            if line[-1].endswith(')'):
                desired_location = line[-2]
            else:
                desired_location = line[-1]
            locations.append(desired_location)
            geolocator = Nominatim(user_agent="taras.yaroshko@ucu.edu.ua")
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.00001)
            location_address = geolocator.geocode(desired_location)
            if location_address == None:
                location_address = geolocator.geocode(','.join(desired_location.split(',')[1:]))
            # print(','.join(desired_location.split(',')[1:]))
            # print(location_address)
            latitudes.append(location_address.latitude) 
            longitudes.append(location_address.longitude)
            movie_place = location_address.latitude, location_address.longitude
            our_place = (49.83826, 24.02324)
            distances.append(haversine(our_place, movie_place))
        # print(movie_place)
        
data = {'Movie': movies,
        # 'Year': years,
        'Location':locations,
        'Latitudes':latitudes,
        'Longitudes':longitudes,
        'Distance':distances
        }
df = pd.DataFrame(data)
minimumvalueindexnumber = df['Distance'].idxmin()
print(df)
print(minimumvalueindexnumber)
list_of_closest = []
for i in range(10):
    mininin = df['Distance'].idxmin()
    element = [df['Movie'][mininin], df['Latitudes'][mininin], df['Longitudes'][mininin]]
    if element not in list_of_closest:
        list_of_closest.append([df['Movie'][mininin], df['Latitudes'][mininin], df['Longitudes'][mininin]])
    df.drop(mininin, inplace=True)
print(list_of_closest)
df.to_csv('file1.csv', index=False, header=False)


path_to_dataset = 'locations.list'
latitude = 40.741059199999995
longitude = -73.98964162240998
map = folium.Map(location= [latitude, longitude], zoom_start=3) 
fg = folium.FeatureGroup('Film_Map')
map.save('Map_1.html')
for index, element in enumerate(list_of_closest):
    fg.add_child(folium.Marker(location=[element[1], element[2]],popup=element[0], icon=folium.Icon()))
map.add_child(fg)
map.save('Map_2.html')

# print(location_address.address)
# print((location_address.latitude, location_address.longitude))