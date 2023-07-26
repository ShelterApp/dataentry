import pandas as pd
import requests
import json
import map_info as mi


# Loads data
def load_compressed(db):
    # Read the CSV
    df = pd.read_csv(db)

    # Drop the duplicates
    df["address1"] = df["address1"].astype(str).str.title()
    df["city"] = df["city"].astype(str).str.title()
    df = df.drop_duplicates(subset=["Organization Name", "address1", "city", "State", "ServiceSummary"], keep="first")

    # Merge services with the same summary, and fill in blanks
    df = df.groupby(["Organization Name", "address1", "city", "State", "zip"]).agg({"ServiceSummary": ", ".join}).reset_index()
    df = df.replace("Nan", "", regex=True)
    df.columns = df.columns.str.lower()
    return df


# Determine if a resource in the CSV is already on Shelter App
def check_database(name, address1, city, state):
    # Remove parentheses from the name
    if "(" in name:
        name = name[0:name.find("(")]

    if ")" in name:
        name = name[0:name.find(")")]

    # Search for a resource on Shelter App
    request_list = requests.get("https://api.shelter.app/services?filter=isApproved&isApproved=true&limit=100&skip=0&search=name,address1,address2,city,state,zip,serviceSummary,category,age&q=" + name)
    data_dict = json.loads(request_list.content)

    # Return true if there is a resource in Shelter App that matches a resource from the CSV
    for data in data_dict:
        if address1 == data["address1"] and city == data["city"] and state == data["state"]:
            return True

    return False


def main():
    # Load the data
    df = load_compressed("hud-data.csv")

    deletion = []
    deleted = 0
    undeleted = 0

    for i in range(len(df)):
        r = df.iloc[i]

        # Add any resource from the CSV that appears on Shelter App to the list of resources to be deleted
        if check_database(r["organization name"], r["address1"], r["city"], r["state"]):
            deletion.append(i)
            deleted += 1
            print("Found a copy of " + r["organization name"] + " in the database " + str(deleted))
        else:
            undeleted += 1
            print("Did not find a copy of " + r["organization name"] + " in the database " + str(undeleted))

    print(str(undeleted) + " will remain and " + str(deleted) + " will be deleted")

    # Delete resources that already appear on Shelter App
    df = df.drop(deletion)

    # Add info on the URLs and schedules of resources
    df = mi.get_expanded_df(df)

    # Create the final CSV to be used on Shelter App
    df.to_csv("hud-data-compressed.csv", sep=",")


if __name__ == "__main__":
    main()
