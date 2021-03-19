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
    confirmed_df = pd.melt(confirmed_df, id_vars=['province/state', 'country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='confirmed')
    death_df = pd.melt(death_df, id_vars=['province/state', 'country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='deaths')
    recovery_df = pd.melt(recovery_df, id_vars=['province/state', 'country/region', 'lat', 'long'],value_vars=dates,var_name='date',value_name='recovered')

    #coverting to dates
    confirmed_df['date'] = pd.to_datetime(confirmed_df['date'])
    death_df['date'] = pd.to_datetime(death_df['date'])
    recovery_df['date'] = pd.to_datetime(recovery_df['date'])

    #Sum of canada confirmed cases, deaths, recovery
    canada_confirmed = confirmed_df[confirmed_df['country/region'] == 'Canada']
    canada_death = death_df[death_df['country/region'] == 'Canada']
    canada_recovery = recovery_df[recovery_df['country/region'] == 'Canada']

    canada_confirmed = canada_confirmed.groupby(['date'])['confirmed'].sum().reset_index()
    canada_confirmed['country/region'] = 'Canada'
    canada_confirmed['province/state'] = 'nan'
    canada_confirmed['lat'] = '56.1304'
    canada_confirmed['long'] = '-106.3468'
    canada_confirmed = canada_confirmed[['province/state', 'country/region', 'lat', 'long', 'date', 'confirmed']]

    canada_death = canada_death.groupby(['date'])['deaths'].sum().reset_index()
    canada_death['country/region'] = 'Canada'
    canada_death['province/state'] = 'nan'
    canada_death['lat'] = '56.1304'
    canada_death['long'] = '-106.3468'
    canada_death = canada_death[['province/state', 'country/region', 'lat', 'long', 'date', 'deaths']]
    
    canada_recovery = canada_recovery.groupby(['date'])['recovered'].sum().reset_index()
    canada_recovery['country/region'] = 'Canada'
    canada_recovery['province/state'] = 'nan'
    canada_recovery['lat'] = '56.1304'
    canada_recovery['long'] = '-106.3468'
    canada_recovery = canada_recovery[['province/state', 'country/region', 'lat', 'long', 'date', 'recovered']]
    

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

def main():    
    confirmed_df, death_df, recovery_df = wwConfirmedDataCollection()
    st.title("Covid-19 🦠 Pandemic Data Visualization")
    displayRawData(confirmed_df, death_df, recovery_df)
    confirmed_df, death_df, recovery_df = dataMassaging(confirmed_df, death_df, recovery_df)
    
    full_table = confirmed_df.merge(right=death_df, how='left',
        on=['province/state', 'country/region', 'date', 'lat', 'long'])
    
    full_table = full_table.merge(right=recovery_df, how='left',
        on=['province/state', 'country/region', 'date', 'lat', 'long'])

    st.write('Data from "CSSEGISandData POST data massaging"')
    st.write(full_table)

if __name__ == "__main__":
    main()
