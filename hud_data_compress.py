import pandas as pd
import requests
import json
import map_testing as mt


def load_compressed(db):
    df = pd.read_csv(db)
    df["address1"] = df["address1"].astype(str).str.title()
    df["city"] = df["city"].astype(str).str.title()
    df = df.drop_duplicates(subset=["Organization Name", "address1", "city", "State", "ServiceSummary"], keep="first")
    df = df.groupby(["Organization Name", "address1", "city", "State", "zip"]).agg({"ServiceSummary": ", ".join}).reset_index()
    df = df.replace("Nan", "", regex=True)
    df.columns = df.columns.str.lower()
    return df


def check_database(name, address1, city, state):
    if "(" in name:
        name = name[0:name.find("(")]

    if ")" in name:
        name = name[0:name.find(")")]

    request_list = requests.get("https://api.shelter.app/services?filter=isApproved&isApproved=true&limit=100&skip=0&search=name,address1,address2,city,state,zip,serviceSummary,category,age&q=" + name)
    data_dict = json.loads(request_list.content)
    for data in data_dict:
        if address1 == data["address1"] and city == data["city"] and state == data["state"]:
            return True

    return False


df = load_compressed("hud-data.csv")

deletion = []
deleted = 0
undeleted = 0
for i in range(len(df)):
    r = df.iloc[i]
    if check_database(r["organization name"], r["address1"], r["city"], r["state"]):
        deletion.append(i)
        deleted += 1
        if i % 1000 == 0:
            print("Found a copy of " + r["organization name"] + " in the database " + str(deleted))
    else:
        undeleted += 1
        if i % 1000 == 0:
            print("Did not find a copy of " + r["organization name"] + " in the database " + str(undeleted))

print(str(undeleted) + " will remain and " + str(deleted) + " will be deleted")
df = df.drop(deletion)
df = mt.get_expanded_df(df)
df.to_csv("hud-data-compressed.csv", sep=",")
