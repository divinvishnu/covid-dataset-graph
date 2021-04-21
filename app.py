import streamlit as st
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk

@st.cache(persist=True, suppress_st_warning=True, allow_output_mutation=True)
def wwConfirmedDataCollection():
    death_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    recovery_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
    confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    confirmed_df = pd.read_csv(confirmed_url)
    death_df = pd.read_csv(death_url)
    recovery_df = pd.read_csv(recovery_url)
    return confirmed_df, death_df, recovery_df

def displayRawData(confirmed_df, death_df, recovery_df):    
    if st.sidebar.checkbox("Display Raw Confirmation Data", False) == True:
        st.write('Data from "CSSEGISandData"')
        st.write('Confirmed Cases')
        st.write(confirmed_df)
        st.write('Death from Cases')
        st.write(death_df)
        st.write('Recovered from Cases')
        st.write(recovery_df)

def dataMassaging(confirmed_df, death_df, recovery_df):
    #converts the column names to lowercase
    confirmed_df = confirmed_df.rename(columns=str.lower)
    death_df = death_df.rename(columns=str.lower)
    recovery_df = recovery_df.rename(columns=str.lower)

    dates = confirmed_df.columns[4:]
    confirmed_df = pd.melt(confirmed_df, id_vars=['country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='confirmed')
    death_df = pd.melt(death_df, id_vars=['country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='deaths')
    recovery_df = pd.melt(recovery_df, id_vars=['country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='recovered')

    #converting to dates
    confirmed_df['date'] = pd.to_datetime(confirmed_df['date'])
    death_df['date'] = pd.to_datetime(death_df['date'])
    recovery_df['date'] = pd.to_datetime(recovery_df['date'])

    #Sum of canada confirmed cases, deaths, recovery
    canada_confirmed = confirmed_df[confirmed_df['country/region'] == 'Canada']
    canada_death = death_df[death_df['country/region'] == 'Canada']
    canada_recovery = recovery_df[recovery_df['country/region'] == 'Canada']

    canada_confirmed = canada_confirmed.groupby(['date'])['confirmed'].sum().reset_index()
    canada_confirmed['country/region'] = 'Canada'
    canada_confirmed['lat'] = '56.1304'
    canada_confirmed['long'] = '-106.3468'
    canada_confirmed = canada_confirmed[['country/region', 'lat', 'long', 'date', 'confirmed']]

    canada_death = canada_death.groupby(['date'])['deaths'].sum().reset_index()
    canada_death['country/region'] = 'Canada'
    canada_death['lat'] = '56.1304'
    canada_death['long'] = '-106.3468'
    canada_death = canada_death[['country/region', 'lat', 'long', 'date', 'deaths']]
    
    canada_recovery = canada_recovery.groupby(['date'])['recovered'].sum().reset_index()
    canada_recovery['country/region'] = 'Canada'
    canada_recovery['lat'] = '56.1304'
    canada_recovery['long'] = '-106.3468'
    canada_recovery = canada_recovery[['country/region', 'lat', 'long', 'date', 'recovered']]
    

    confirmed_df = confirmed_df[confirmed_df['country/region']!='Canada']
    death_df = death_df[death_df['country/region']!='Canada']
    recovery_df = recovery_df[recovery_df['country/region']!='Canada']

    
    new_confirmed_df = confirmed_df.append(canada_confirmed,ignore_index=True)
    new_confirmed_df.sort_values(['date','country/region'], ascending=[True, True], inplace=True)
    new_confirmed_df = new_confirmed_df.reset_index(drop=True)

    new_death_df = death_df.append(canada_death,ignore_index=True)
    new_death_df.sort_values(['date','country/region'], ascending=[True, True], inplace=True)
    new_death_df = new_death_df.reset_index(drop=True)

    new_recovery_df = recovery_df.append(canada_recovery,ignore_index=True)
    new_recovery_df.sort_values(['date','country/region'], ascending=[True, True], inplace=True)
    new_recovery_df = new_recovery_df.reset_index(drop=True)

    if st.sidebar.checkbox("Display combined join data after canada calculation", False) == True:
        st.write("JOINING DATA TOGETHER ON DATE")
        st.write("Confirmed")
        st.write(new_confirmed_df)
        st.write("Dead")
        st.write(new_death_df)
        st.write("Recovered")
        st.write(new_recovery_df)

    return new_confirmed_df, new_death_df, new_recovery_df

def rgb(minimum, maximum, value):
            minimum, maximum = float(minimum), float(maximum)
            ratio = 2 * (value-minimum) / (maximum - minimum)
            b = int(max(0, 255*(1 - ratio)))
            r = int(max(0, 255*(ratio - 1)))
            g = 255 - b - r
            return r, g, b

def main():    
    confirmed_df, death_df, recovery_df = wwConfirmedDataCollection()
    st.title("Covid-19 🦠 Pandemic Data Visualization")
    displayRawData(confirmed_df, death_df, recovery_df)
    confirmed_df, death_df, recovery_df = dataMassaging(confirmed_df, death_df, recovery_df)
    
    full_table = confirmed_df.merge(right=death_df, how='left',
        on=['country/region', 'date', 'lat', 'long'])
    
    full_table = full_table.merge(right=recovery_df, how='left',
        on=['country/region', 'date', 'lat', 'long'])

    st.write('Data from "CSSEGISandData POST data massaging"')
    full_table = full_table.rename(columns={'long':'lon'})
    full_table['recovered'] = full_table['recovered'].fillna(0)
    rows_with_zero_location = full_table['country/region'].str.contains('Diamond Princess') | full_table['country/region'].str.contains('MS Zaandam')
    full_table = full_table[~(rows_with_zero_location)]
    # st.write(full_table.isna().sum())
    # full_table.drop(columns=['province/state'], axis=1)

    # removing the time associated with date_time to just date to help reduce complexity in data. 
    full_table['date'] = full_table['date'].dt.date

    full_table = full_table.rename(columns={'country/region':'location'})
    user_selectionbox_input = st.selectbox("Select an option", ['Global', 'Select from list of countries'])
    if user_selectionbox_input == 'Select from list of countries':
        list_of_countries = full_table['location'].unique()
        selected_countries = st.multiselect('Select countries', list_of_countries)

        mask_countries = full_table['location'].isin(selected_countries)
        full_table = full_table[mask_countries]
        st.write(full_table)
        temp = pd.DataFrame(full_table, columns=['date','confirmed','deaths','recovered'])
        temp = temp.rename(columns={'date':'index'}).set_index('index')
        st.line_chart(temp)
    else:
        min_date = datetime.datetime(2020,1,1)
        max_date = datetime.date(2022,1,1)

        selected_date = st.date_input("Pick a date", min_value=min_date, max_value=max_date)
        "The date selected:", selected_date
        full_table = full_table[full_table['date']== selected_date]
        temp = pd.DataFrame(full_table, columns=['location','lat', 'lon','confirmed'])
        temp =  temp.reset_index()
        st.write(temp)
        st.write(temp['confirmed'].max())

        

        INITIAL_VIEW_STATE = pdk.ViewState(
             latitude=55.3781,
             longitude=-3.436,
             zoom=1,
             pitch=25,
        )

        # view = pdk.data_utils.compute_view(temp[["lon","lat"]])
        column_layer = pdk.Layer(
                "ColumnLayer",
                data=temp,
                get_position=["lon", "lat"],
                radius=50000,
                get_elevation="confirmed",
                elevation_scale=.70,
                get_fill_color = ["255,255, confirmed*.1"],
                get_line_color = [255,45,255],
                filled = True,
                pickable=True,
                extruded=True,
                auto_highlight=True,          
        )
        TOOLTIP = {
            "html": "<b>{confirmed}</b> Confirmed Cases <br>{location}",
            "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
        }

        r = pdk.Deck(
            column_layer,
            # map_style=pdk.map_styles.SATELLITE,
            map_style="mapbox://styles/mapbox/light-v9",
            map_provider="mapbox",
            initial_view_state = INITIAL_VIEW_STATE,
            tooltip= TOOLTIP
        )
        st.pydeck_chart(r)
        # r.to_html("test.html", open_browser=True, notebook_display=False)

if __name__ == "__main__":
    main()
