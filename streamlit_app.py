import streamlit as st
import pandas as pd
from sodapy import Socrata
import pymongo
import pprint

client = pymongo.MongoClient(
    "mongodb+srv://minhyukc:Alsgur6209!@saferla.ptbmk.mongodb.net/myFirstDatabase?retryWrites=true&w=majorty")
data_obj = client.saferla.saferla.find()

def get_loc():
    loc_list = []
    for t in data_obj:
        loc_list.append([t['lat'],t['lon']])
    df = pd.DataFrame(loc_list, columns=['lat','lon'])
    return df

def get_time():
    time_list = []
    for t in data_obj:
        time_list.append(t['time_occ'])
    df = pd.DataFrame(time_list, columns=['time_occ'])
    return df

def get_age():
    age_list = []
    for t in data_obj:
        age_list.append(t['vict_age'])
    df = pd.DataFrame(age_list, columns=['vict_age'])
    return df

def get_crime():

def get_gender():

def main():
    #client_socrata = Socrata("data.lacity.org", "iXEwpGFYBErwQDvsIB1TXnXtW", username="minhyukc@usc.edu", password="Alsgur6209!")
    #results = client_socrata.get("2nrs-mtv8", limit=441000)
    #mydb = client["saferla"]
    #my_collection = mydb['saferla']
    #my_collection.insert_many(results)

    #print(temp_list)


    st.title('Los Angeles Crime Map')



if __name__ == "__main__":
    main()
