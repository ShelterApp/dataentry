import googlemaps
import pprint
from datetime import datetime

map_client = googlemaps.Client(key="<YOUR KEY>")


def get_place_info(location_name):
    try:
        response = map_client.places(query=location_name)
        results = response.get("results")
        if len(results) == 0:
            return None
        place_id = results[0]["place_id"]
        place_details = map_client.place(place_id=place_id)
        return place_details["result"]
    except Exception as e:
        print(e)
        return None


def get_schedule(schedule_list):
    if schedule_list is not None and "current_opening_hours" in schedule_list:
        schedule = ""
        for day in schedule_list["current_opening_hours"]["weekday_text"]:
            if isinstance(day, str):
                schedule = schedule + day.replace('\u2009', '').replace('\u202f', '') + " "
        return schedule
    return ""


def get_expanded_df(df):
    scheds = []
    urls = []
    for i in range(len(df)):
        place_details = get_place_info(df.iloc[i]["organization name"] + " " + df.iloc[i]["address1"] + " " + df.iloc[i]["city"] + " " + df.iloc[i]["state"] + " " + str(df.iloc[i]["zip"]))
        print(i)
        scheds.append(get_schedule(place_details))
        if place_details is not None and "website" in place_details:
            urls.append(place_details["website"])
        else:
            urls.append("")
        if i % 1000 == 0:
            print(place_details)
    print("There are " + str(len(df)) + " entries")
    print("There are " + str(len(scheds)) + " schedules")
    print("There are " + str(len(urls)) + " URLs")
    df["hours"] = scheds
    df["website"] = urls
    return df
