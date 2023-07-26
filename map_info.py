import googlemaps
import config

map_client = googlemaps.Client(key=config.api_key)


# Get info on a location on Google Maps
def get_place_info(location_name):
    try:
        # Use the Google Maps API to get raw data on a location
        response = map_client.places(query=location_name)
        results = response.get("results")

        # Stop if there is no info on a location on Google Maps
        if len(results) == 0:
            return None

        # Retrieve specific details on a location from Google Maps
        place_id = results[0]["place_id"]
        place_details = map_client.place(place_id=place_id)
        return place_details["result"]

    # Throw an exception something goes wrong with the request
    except Exception as e:
        print(e)
        return None


# Get the schedule of a location on Google Maps
def get_schedule(schedule_list):
    if schedule_list is not None and "current_opening_hours" in schedule_list:
        schedule = ""

        # Get hourly information for each day of the week
        for day in schedule_list["current_opening_hours"]["weekday_text"]:
            if isinstance(day, str):
                # Format the text in a way that is readable on the Shelter App dataset
                schedule = schedule + day.replace('\u2009', '').replace('\u202f', '') + " "

        return schedule
    return ""


# Add URLs and schedules to the dataframe used to make the final CSV
def get_expanded_df(df):
    scheds = []
    urls = []

    for i in range(len(df)):
        # Get specific details on a location on Google Maps and add the schedule to the list of schedules
        place_details = get_place_info(df.iloc[i]["organization name"] + " " + df.iloc[i]["address1"] + " " + df.iloc[i]["city"] + " " + df.iloc[i]["state"] + " " + str(df.iloc[i]["zip"]))
        print(i)
        scheds.append(get_schedule(place_details))

        # Get the URL of a location on Google Maps
        if place_details is not None and "website" in place_details:
            urls.append(place_details["website"])
        else:
            urls.append("")

        print(place_details)

    print("There are " + str(len(df)) + " entries")
    print("There are " + str(len(scheds)) + " schedules")
    print("There are " + str(len(urls)) + " URLs")
    df["hours"] = scheds
    df["website"] = urls
    return df
