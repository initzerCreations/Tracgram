import instaloader
import pandas as pd
import folium
from folium.plugins import HeatMap
import time
import random
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np


class Tracgram:
    def __init__(self, nickname, password, objective, path_to_csv):
        self.nickname = nickname
        self.password = password
        self.objective = objective
        self.path_to_csv = path_to_csv
        self.L = instaloader.Instaloader()

    # Obtain profile posts
    def get_profile_posts(self):
        self.L.login(str(self.nickname), str(self.password))
        profile = instaloader.Profile.from_username(self.L.context, str(self.objective))
        posts = profile.get_posts()
        return posts

    # Create a csv file with the location data {location_name, date, latitude , longitude}
    def retreive_location_data(self, posts):
        # Init variables
        counter = 0
        with open(self.path_to_csv, "w", encoding="utf-8") as file:
            file.write("location_name,date,latitude,longitude\n")
            for post in posts:
                try:
                    print("Posts processed: " + str(counter))
                    counter = counter + 1
                    
                    if post.location != None:
                        location_name = post.location.name                
                        date = post.date_utc
                        latitude = post.location.lat
                        longitude = post.location.lng
                        
                        # Remove the commas from the location name to avoid errors
                        location_name = location_name.replace(",", " ")
                        
                        file.write(location_name + "," + str(date) + "," + str(latitude) + "," + str(longitude) + "\n")
                    else:
                        sleep_time = random.randint(7, 11)
                        time.sleep(sleep_time)

                except Exception as e:
                    # Ignore the exception and continue to the next post, this could be procuded by Instagram trying to block the scrapper
                    self.L.InstaloaderContext.error_catcher(e)
                    pass

    def populate_map_and_graph(self):
        # Creates the map
        map_obj = folium.Map(location=[0, 0], zoom_start=2)
        folium.TileLayer('cartodbdark_matter').add_to(map_obj)
        
        # Read the csv file
        df= pd.read_csv(self.path_to_csv)

        # Get the locations and the weights
        locations = []
        names = []
        for i in range(len(df)):
            latitude = df.values[i][2]
            longitude = df.values[i][3]
            names.append([df.values[i][0]])
            
            if latitude != "None" and longitude != "None":
                locations.append([latitude, longitude])
                # We also create a marker in the map showing specific data with a link to google maps
                link = "https://www.google.com/maps/search/" + str(df.values[i][0]) + "/"
                marker_data = '<a href="'+str(link)+'">'+ str(df.values[i][0]) +'</a>' + "\n" + str(df.values[i][1])
                folium.Marker([latitude, longitude], popup=marker_data).add_to(map_obj)
            else:
                continue

        locations_weight = []
        for loc in locations:
            weight = locations.count(loc)
            if loc not in locations_weight:
                loc.append(weight)
                locations_weight.append(loc)

        locations_name_weight = []   
        for n in names:
            weight_n = names.count(n)
            if n not in locations_name_weight:
                n.append(weight_n)
                locations_name_weight.append(n)
    
        # Generate the heatmap using the locations and the weights
        HeatMap(locations_weight).add_to(map_obj)
        map_obj.save("location_heatmap.html")
        
        # Generate the graph
        name_tags = []
        weight_n = []
        for nam in names:
            name_tags.append(nam[0])
            weight_n.append(nam[1])

        y_pos = np.arange(len(name_tags))
        plt.barh(y_pos, weight_n, align='center', alpha=0.5)
        plt.yticks(y_pos, name_tags, rotation=45)
        plt.ylabel('Locations')
        plt.title('Number of posts per location')
        plt.tick_params(axis='y', which='major', labelsize=2)
        plt.savefig("posts_per_location.png", dpi=1800)


def main():
    # Change the parameters with your own data
    tracgram = Tracgram("YOUR NICKNAME", "YOUR PASSWORD", "OBJECTIVE NICKNAME", "results.csv") # results.csv is the name of the csv file that will be created
    # Obtain the location data
    tracgram.retreive_location_data(tracgram.get_profile_posts())
    # Generates location_heatmap.html and posts_per_location.png
    tracgram.populate_map_and_graph()

if __name__ == "__main__":
    main()
