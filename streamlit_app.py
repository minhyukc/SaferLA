import config
import streamlit as st
import pandas as pd
import pydeck as pdk
import pymongo
from sodapy import Socrata

# client_socrata = Socrata("data.lacity.org", "iXEwpGFYBErwQDvsIB1TXnXtW", username=config.username, password=config.password)
# results = client_socrata.get("2nrs-mtv8", limit=441000)
# mydb = client["saferla"]
# my_collection = mydb['saferla']
# my_collection.insert_many(results)
client = pymongo.MongoClient(
    "mongodb+srv://minhyukc:" + config.password + "@saferla.ptbmk.mongodb.net/myFirstDatabase?retryWrites=true&w=majorty")


def get_time(obj):
    data_obj = obj
    data_list = list()
    for t in data_obj:
        data_list.append(t)
    if not data_list:
        return pd.DataFrame()
    df_time_occ = pd.DataFrame(data_list)

    time_occ = list()
    for i in df_time_occ['time_occ']:
        x = int(i[:2])  # Extract only the hours
        if x == 0:
            x = 24
        time_occ.append(x)

    time_count = {}
    for p in range(1, 25, 1):
        counter = 0
        for q in time_occ:
            if q == p:
                counter += 1
        time_count[p] = counter

    time_dict = {}
    for j in range(1, 25, 1):
        time_dict[j] = 0

    for k in range(1, 25, 1):
        if k in time_count.keys():
            time_dict[k] = time_count[k]

    df = pd.DataFrame.from_dict(time_dict, orient='index')
    return df


def conditioned_map(gender=None, age=None):
    argument_list = [gender, age]
    argument_name = ["vict_sex", "vict_age"]
    final_dict = {}

    for i in range(0, len(argument_list)):
        if argument_list[i] is not None:
            if argument_list[i] != "B" or argument_list[i] != '0':
                final_dict[argument_name[i]] = argument_list[i]
    if age == '0':
        data_obj = client.saferla.saferla.find(final_dict, {"lat": 1, "lon": 1, "_id": 0})
        data_obj_time = client.saferla.saferla.find(final_dict, {"time_occ": 1, "_id": 0})
        data_list = list()
        for t in data_obj:
            data_list.append(t)
        df = pd.DataFrame(data_list).astype('float64')

        time_df = get_time(data_obj_time)
        return df, time_df

    else:  # age is not none, which means we have an age input
        data_obj = client.saferla.saferla.find(final_dict, {"lat": 1, "lon": 1, "_id": 0})
        data_obj_time = client.saferla.saferla.find(final_dict, {"time_occ": 1, "_id": 0})
        data_list = list()
        for t in data_obj:
            data_list.append(t)
        df = pd.DataFrame(data_list).astype('float64')
        time_df = get_time(data_obj_time)

        return df, time_df


def crime_type():
    data_obj = client.saferla.saferla.find({}, {"vict_sex": 1, "crm_cd_desc": 1, "_id": 0})
    data_list = list()
    for t in data_obj:
        data_list.append(t)
    df = pd.DataFrame(data_list)
    df_gender = df['vict_sex'].value_counts()
    n_m = df_gender.iloc[0]
    n_f = df_gender.iloc[1]
    total = n_m + n_f

    df_crime = df['crm_cd_desc']
    return df_crime.value_counts(), [n_m / total, n_f / total]


def main():
    st.set_page_config(layout="wide")

    with st.sidebar:
        age_input = str(st.number_input("Enter a victim's age", min_value=0, max_value=98, value=0))
        st.write('0 shows the entire data.')
        st.write("If there's no point shown, then there has been no incident for the specified victim age")
        gender_input = st.selectbox("Choose a victim's gender", ('Male', 'Female', 'Both'))[0].upper()
        map_input = st.radio(
            "Choose the map type",
            ('Grid', 'Scatter')
        )

    with st.container():
        st.title('Los Angeles Crime Map')
        map_df = conditioned_map(gender=gender_input, age=age_input)[0]
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
        if len(conditioned_map(gender=gender_input, age=age_input)[1]) != 0:
            time_occ = conditioned_map(gender=gender_input, age=age_input)[1]
            time_occ.rename(columns={0: 'Crime Occurred'}, inplace=True)
            st.bar_chart(time_occ)
        else:
            st.write('There is no data for the specified age and gender.')

    with st.container():
        st.title('Top 10 Common Crime Types')
        df = crime_type()[0]
        df.rename('Crime Types', inplace=True)
        st.dataframe(df.head(10))

    with st.container():
        st.title('Crime Statistics')
        percentages = crime_type()[1]
        male_perc = round(percentages[0] * 100, 1)
        female_perc = round(percentages[1] * 100, 1)
        st.metric('Male Victim Rate', str(male_perc) + "%")
        st.metric('Female Victim Rate', str(female_perc) + "%")


if __name__ == "__main__":
    main()
