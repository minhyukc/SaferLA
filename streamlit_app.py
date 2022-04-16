import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from sodapy import Socrata
import pymongo
import pprint
from datetime import time, datetime
import matplotlib.pyplot as plt
import matplotlib.dates

client = pymongo.MongoClient(
    "mongodb+srv://minhyukc:Alsgur6209!@saferla.ptbmk.mongodb.net/myFirstDatabase?retryWrites=true&w=majorty")


def conditioned_map(gender=None, age=None):
    argument_list = [gender, age]
    argument_name = ["vict_sex", "vict_age"]
    final_dict = {}

    for i in range(0, len(argument_list)):
        if argument_list[i] is not None:
            if argument_list[i] != "B":
                final_dict[argument_name[i]] = argument_list[i]

    if age == 0:
        data_obj = client.saferla.saferla.find({"$and":[{"vict_age": {"$gt": "0", "$lt": "120"}}, final_dict]},
                                                {"lat": 1, "lon": 1, "_id": 0})
        data_list = list()
        for t in data_obj:
            data_list.append(t)
        df = pd.DataFrame(data_list).astype('float64')
        return df

    else:  # age is not none, which means we have an age input
        data_obj = client.saferla.saferla.find(final_dict, {"lat": 1, "lon": 1, "_id": 0})
        data_list = list()
        for t in data_obj:
            data_list.append(t)
        df = pd.DataFrame(data_list).astype('float64')
        return df


def get_time():
    data_obj = client.saferla.saferla.find({}, {"time_occ": 1, "_id": 0})
    data_list = list()
    for t in data_obj:
        data_list.append(t)
    df_time_occ = pd.DataFrame(data_list)
    time_occ = pd.to_datetime(df_time_occ['time_occ'], format="%H%M").dt.time.value_counts()
    df_final_time = pd.DataFrame()
    df_final_time['time_occ'] = time_occ.index
    df_final_time['count'] = list(time_occ)

    return df_final_time


def main():
    # client_socrata = Socrata("data.lacity.org", "iXEwpGFYBErwQDvsIB1TXnXtW", username="minhyukc@usc.edu", password="Alsgur6209!")
    # results = client_socrata.get("2nrs-mtv8", limit=441000)
    # mydb = client["saferla"]
    # my_collection = mydb['saferla']
    # my_collection.insert_many(results)

    with st.sidebar:
        age_input = str(st.number_input("Enter a victim's age", value=0))
        gender_input = st.selectbox("Choose a victim's gender", ('Male', 'Female', 'Both'))[0].upper()
    get_time()
    map_df = conditioned_map(gender=gender_input, age=age_input)
    with st.container():
        st.title('Los Angeles Crime Map')
        # st.write(map_df.count())
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=34.05,
                longitude=-118.24,
                zoom=10,
                pitch=50,
            ),
            layers=[
                # pdk.Layer(
                #     'HexagonLayer',
                #     data=map_df,
                #     get_position='[lon, lat]',
                #     radius=200,
                #     elevation_scale=4,
                #     elevation_range=[0, 1000],
                #     pickable=True,
                #     extruded=True,
                # ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=map_df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=200,
                ),
            ],
        ))

    time_occ = get_time()
    with st.container():
        time_occ.plot(x='time_occ', y='count', kind='scatter')
        plt.show()
if __name__ == "__main__":
    main()
