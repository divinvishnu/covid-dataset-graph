import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        st.write(confirmed_df)
        st.write(death_df)
        st.write(recovery_df)

def dataMassaging(confirmed_df, death_df, recovery_df):
    confirmed_df = confirmed_df.rename(columns=str.lower)
    death_df = death_df.rename(columns=str.lower)
    recovery_df = recovery_df.rename(columns=str.lower)

    dates = confirmed_df.columns[4:]
    confirmed_df = pd.melt(confirmed_df, id_vars=['province/state', 'country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='confirmed')
    death_df = pd.melt(death_df, id_vars=['province/state', 'country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='deaths')
    recovery_df = pd.melt(recovery_df, id_vars=['province/state', 'country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='recovered')

    #if(confirmed_df['country/region'] == 'Canada'):
       # dateOf = confirmed_df['date']

    confirmed_df['date'] = pd.to_datetime(confirmed_df['date'])
    death_df['date'] = pd.to_datetime(death_df['date'])
    recovery_df['date'] = pd.to_datetime(recovery_df['date'])

    canada = confirmed_df[confirmed_df['country/region'] == 'Canada']
    st.write(canada)

    temp_df = canada.groupby(['date'])['confirmed'].sum()
    st.write(temp_df)    

    confirmed_df = confirmed_df[confirmed_df['country/region']!='Camada']
    death_df = death_df[death_df['country/region']!='Camada']
    recovery_df = recovery_df[recovery_df['country/region']!='Camada']

    confirmed_df = confirmed_df.append({'nan', 'Canada', 56.1304, -106.3468})    

    return confirmed_df, death_df, recovery_df

def main():    
    confirmed_df, death_df, recovery_df = wwConfirmedDataCollection()
    st.title("Covid-19 🦠 Pandemic Data Visualization")
    displayRawData(confirmed_df, death_df, recovery_df)
    confirmed_df, death_df, recovery_df = dataMassaging(confirmed_df, death_df, recovery_df)
    

    st.write('Data from "CSSEGISandData"')
    st.write(confirmed_df)
    st.write(death_df)
    st.write(recovery_df)

if __name__ == "__main__":
    main()
