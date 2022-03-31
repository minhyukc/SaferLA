import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from sodapy import Socrata
import pymongo
import pprint
from datetime import datetime

client = pymongo.MongoClient(
    "mongodb+srv://minhyukc:Alsgur6209!@saferla.ptbmk.mongodb.net/myFirstDatabase?retryWrites=true&w=majorty")


def conditioned_map(gender=None, age=None, time=None, crime_type=None):
    start = datetime.now()
    argument_list = [gender, age, time, crime_type]
    argument_name = ["vict_sex", "vict_age", "time_occ", "crm_cd_desc"]
    final_dict = {}

    for i in range(0, len(argument_list)):
        if argument_list[i] is not None:
            final_dict[argument_name[i]] = argument_list[i]
    data_obj = client.saferla.saferla.find(final_dict, {"lat": 1, "lon": 1, "_id": 0})
    data_list = list()
    for t in data_obj:
        data_list.append(t)
    df = pd.DataFrame(data_list)
    print(datetime.now() - start)
    return df


def main():
    # client_socrata = Socrata("data.lacity.org", "iXEwpGFYBErwQDvsIB1TXnXtW", username="minhyukc@usc.edu", password="Alsgur6209!")
    # results = client_socrata.get("2nrs-mtv8", limit=441000)
    # mydb = client["saferla"]
    # my_collection = mydb['saferla']
    # my_collection.insert_many(results)



    # st.title('Los Angeles Crime Map')

    df = conditioned_map("F", "36", "2230")
    # print(df)
    # st.write(df)
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=34.05,
            longitude=-118.24,
            zoom=5,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=df,
                get_position='[lat, lon]',
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[lat, lon]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
        ],
    ))


if __name__ == "__main__":
    main()
