import streamlit as st
import pandas as pd
import pydeck as pdk
import pymongo
from sodapy import Socrata


# client_socrata = Socrata("data.lacity.org", "iXEwpGFYBErwQDvsIB1TXnXtW", username="minhyukc@usc.edu", password="Alsgur6209!")
# results = client_socrata.get("2nrs-mtv8", limit=441000)
# mydb = client["saferla"]
# my_collection = mydb['saferla']
# my_collection.insert_many(results)
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
        data_obj = client.saferla.saferla.find({"$and": [{"vict_age": {"$gt": "0", "$lt": "120"}}, final_dict]},
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
    time_occ = list()

    for i in df_time_occ['time_occ']:
        i = int(i[:2])
        if i == 0:
            i = 24
        time_occ.append(i)

    df_final = pd.DataFrame(time_occ).value_counts().sort_index(axis=0)
    time_dict = {}
    for i in range(1, 25, 1):
        time_dict[i] = df_final.iloc[i-1]

    df = pd.DataFrame.from_dict(time_dict, orient='index')
    print(df)
    return df


def main():
    st.set_page_config(layout="wide")

    with st.sidebar:
        age_input = str(st.number_input("Enter a victim's age", min_value=0, max_value=98, value=0))
        gender_input = st.selectbox("Choose a victim's gender", ('Male', 'Female', 'Both'))[0].upper()
        map_input = st.radio(
            "Choose the map type",
            ('Grid', 'Scatter')
        )


    with st.container():
        st.title('Los Angeles Crime Map')
        map_df = conditioned_map(gender=gender_input, age=age_input)
        if map_input == 'Grid':
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v9',
                initial_view_state=pdk.ViewState(
                    latitude=34.05,
                    longitude=-118.24,
                    zoom=10,
                    pitch=70,
                ),
                layers=[
                    pdk.Layer(
                        "GridLayer",
                        data=map_df,
                        pickable=True,
                        extruded=True,
                        cell_size=200,
                        elevation_scale=4,
                        get_position=['lon', 'lat'],
                    ),
                ],
            ))
        elif map_input == 'Scatter':
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v9',
                initial_view_state=pdk.ViewState(
                    latitude=34.05,
                    longitude=-118.24,
                    zoom=10,
                    pitch=70,
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=map_df,
                        pickable=True,
                        opacity=0.8,
                        stroked=False,
                        filled=True,
                        radius_scale=6,
                        radius_min_pixels=2,
                        radius_max_pixels=100,
                        line_width_min_pixels=1,
                        get_position=['lon', 'lat'],
                        get_fill_color=[255, 255, 0],
                        get_line_color=[0, 0, 0],
                    ),
                ],
        ))

    st.markdown('#')
    st.markdown('#')
    st.markdown('#')

    with st.container():
        time_occ = get_time()
        time_occ.rename(columns={0: 'Crime Occurred'}, inplace=True)
        st.bar_chart(time_occ)


if __name__ == "__main__":
    main()
