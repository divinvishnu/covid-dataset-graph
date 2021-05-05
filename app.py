import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def wwConfirmedDataCollection():
    death_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    recovery_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
    confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    confirmed_df = pd.read_csv(confirmed_url)
    death_df = pd.read_csv(death_url)
    recovery_df = pd.read_csv(recovery_url)
    return confirmed_df, death_df, recovery_df

def displayRawData(confirmed_df, death_df, recovery_df):
    if st.sidebar.checkbox("Display Raw Data From CSSEGIS", False) == True:
        st.write('Data from "CSSEGISandData"')
        st.write("Confirmed Cases")
        st.write(confirmed_df)
        st.write("Death from Cases")
        st.write(death_df)
        st.write("Recovered from Cases")
        st.write(recovery_df)

def dataMassaging(confirmed_df, death_df, recovery_df):
    # converts the column names to lowercase
    confirmed_df = confirmed_df.rename(columns=str.lower)
    death_df = death_df.rename(columns=str.lower)
    recovery_df = recovery_df.rename(columns=str.lower)

    dates = confirmed_df.columns[4:]
    confirmed_df = pd.melt(
        confirmed_df,
        id_vars=["country/region", "lat", "long"],
        value_vars=dates,
        var_name="date",
        value_name="confirmed",
    )
    # st.write(confirmed_df.dtypes)   
    death_df = pd.melt(
        death_df,
        id_vars=["country/region", "lat", "long"],
        value_vars=dates,
        var_name="date",
        value_name="deaths",
    )
    recovery_df = pd.melt(
        recovery_df,
        id_vars=["country/region", "lat", "long"],
        value_vars=dates,
        var_name="date",
        value_name="recovered",
    )

    # converting to dates
    confirmed_df["date"] = pd.to_datetime(confirmed_df["date"])
    death_df["date"] = pd.to_datetime(death_df["date"])
    recovery_df["date"] = pd.to_datetime(recovery_df["date"])

    # Sum of canada confirmed cases, deaths, recovery
    canada_confirmed = confirmed_df[confirmed_df["country/region"] == "Canada"]
    canada_death = death_df[death_df["country/region"] == "Canada"]
    canada_recovery = recovery_df[recovery_df["country/region"] == "Canada"]

    canada_confirmed = (
        canada_confirmed.groupby(["date"])["confirmed"].sum().reset_index()
    )
    
    canada_confirmed["country/region"] = "Canada"
    canada_confirmed["lat"] = 56.1304
    canada_confirmed["long"] = -106.3468
    canada_confirmed = canada_confirmed[
        ["country/region", "lat", "long", "date", "confirmed"]
    ]
     
    canada_death = canada_death.groupby(["date"])["deaths"].sum().reset_index()
    canada_death["country/region"] = "Canada"
    canada_death["lat"] = 56.1304
    canada_death["long"] = -106.3468
    canada_death = canada_death[["country/region", "lat", "long", "date", "deaths"]]

    canada_recovery = canada_recovery.groupby(["date"])["recovered"].sum().reset_index()
    canada_recovery["country/region"] = "Canada"
    canada_recovery["lat"] = 56.1304
    canada_recovery["long"] = -106.3468
    canada_recovery = canada_recovery[
        ["country/region", "lat", "long", "date", "recovered"]
    ]

    confirmed_df = confirmed_df[confirmed_df["country/region"] != "Canada"]
    death_df = death_df[death_df["country/region"] != "Canada"]
    recovery_df = recovery_df[recovery_df["country/region"] != "Canada"]

    new_confirmed_df = confirmed_df.append(canada_confirmed, ignore_index=True)
    new_confirmed_df.sort_values(
        ["date", "country/region"], ascending=[True, True], inplace=True
    )
    new_confirmed_df = new_confirmed_df.reset_index(drop=True)

    new_death_df = death_df.append(canada_death, ignore_index=True)
    new_death_df.sort_values(
        ["date", "country/region"], ascending=[True, True], inplace=True
    )
    new_death_df = new_death_df.reset_index(drop=True)

    new_recovery_df = recovery_df.append(canada_recovery, ignore_index=True)
    new_recovery_df.sort_values(
        ["date", "country/region"], ascending=[True, True], inplace=True
    )
    new_recovery_df = new_recovery_df.reset_index(drop=True)

    if (
        st.sidebar.checkbox(
            "Display join data after canada calculation", False
        )
        == True
    ):
        st.write("JOINING DATA TOGETHER ON DATE")
        st.write("Confirmed")
        st.write(new_confirmed_df)
        st.write("Dead")
        st.write(new_death_df)
        st.write("Recovered")
        st.write(new_recovery_df)

    return new_confirmed_df, new_death_df, new_recovery_df

#utilizing solution from https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings-in-python 
def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )

def mergeDataAndDataCorrection(confirmed, death, recovery):
    full_table = confirmed.merge(
        right=death, how="left", on=["country/region", "date", "lat", "long"]
    )

    full_table = full_table.merge(
        right=recovery, how="left", on=["country/region", "date", "lat", "long"]
    )

    full_table = full_table.rename(columns={"long": "lon"})
    full_table["recovered"] = full_table["recovered"].fillna(0)
    rows_with_zero_location = full_table["country/region"].str.contains(
        "Diamond Princess"
    ) | full_table["country/region"].str.contains("MS Zaandam")
    full_table = full_table[~(rows_with_zero_location)]

    if full_table.isna().sum().any() > 0:
        full_table.dropna(subset=["lat", "lon"], inplace=True)

    # checking to find nan is unusual spots
    # st.write(full_table.isna().sum())
    # st.write(full_table)
    # full_table.drop(columns=['province/state'], axis=1)

    # removing the time associated with date_time to just date to help reduce complexity in data.
    full_table["date"] = full_table["date"].dt.date

    full_table = full_table.rename(columns={"country/region": "location"})
    return full_table

def altairLineChartGraphing(graphTitle, source):
    source = source.rename(columns={"date": "index"}).set_index("index")
    filtered = st.multiselect("Filter Data", options=list(source.columns), default=list(source.columns))

    chart = alt.Chart(source.reset_index()).transform_fold(
        filtered,
        as_=['Reported', 'cases']
    ).mark_line(interpolate='basis').encode(
        alt.X('index:T',title='Dates'),
        alt.Y('cases:Q',title='Cases'),
        color='Reported:N',
        tooltip=[alt.Tooltip('index:T', title='Date'), 'cases:Q', 'Reported:N']
    )

    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                fields=['index'], empty='none')

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(source.reset_index()).transform_fold(
        filtered,
        as_=['Reported', 'cases']
    ).mark_point().encode(
        x='index:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = chart.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = chart.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'cases:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(source.reset_index()).transform_fold(
        filtered,
        as_=['Reported', 'cases']
    ).mark_rule(color='gray').encode(
        x='index:T',
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    layerChart = alt.layer(chart, selectors, points, rules, text,
                            width=800, height = 400, title=graphTitle)
    return layerChart

def main():
    st.set_page_config(layout="wide") 
    st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',
             unsafe_allow_html=True)

    confirmed_df, death_df, recovery_df = wwConfirmedDataCollection()
    st.title("Covid-19 🦠 Pandemic Data Visualization")
    displayRawData(confirmed_df, death_df, recovery_df)
    confirmed_df, death_df, recovery_df = dataMassaging(
        confirmed_df, death_df, recovery_df
    )
    full_table = mergeDataAndDataCorrection(confirmed_df, death_df, recovery_df)

    st.write('\nData from "CSSEGISandData POST data massaging"')
    
    user_selectionbox_input = st.selectbox(
        "Select an option", ["Global", "Select from list of countries"]
    )
    min_date_found = full_table["date"].min()
    max_date_found = full_table["date"].max()

    selected_date = st.date_input(
        "Pick a date",
        (min_date_found, max_date_found)
    )
    if len(selected_date) == 2:
        
        if user_selectionbox_input == "Select from list of countries":
            full_table = full_table[(full_table['date'] >= selected_date[0]) & (full_table['date'] <= selected_date[1])]
            
            # full_table = full_table[full_table["date"] == (between(selected_date[0], selected_date[1]))]
            list_of_countries = full_table["location"].unique()
            selected_country = st.selectbox("Select country", list_of_countries)

            mask_countries = full_table["location"] == (selected_country)
            full_table = full_table[mask_countries]

            # Adding new cases to the table for graphing
            full_table["new_confirmed"] = full_table["confirmed"].diff(1).fillna(0)
            full_table["new_recovered"] = full_table["recovered"].diff(1).fillna(0)
            full_table["new_deaths"] = full_table["deaths"].diff(1).fillna(0)
            

            user_input = st.selectbox(
                "Select an option", ["Total Number of Cases", "New Cases Per Day"]
            )
            st.write(full_table)
            if user_input == "New Cases Per Day":
                source = pd.DataFrame(full_table, columns=["date", "new_confirmed", "new_recovered", "new_deaths"])
                title = f"New Cases Per Day for {selected_country}"
            else:
                source = pd.DataFrame(
                    full_table, columns=["date", "confirmed", "deaths", "recovered"]
                )
                title = f"Total reported cases for {selected_country}"
            
            st.altair_chart(altairLineChartGraphing(title, source), use_container_width=True)    

        else:
            full_table = full_table[full_table["date"] == selected_date[1]]
            confirmed_source = pd.DataFrame(full_table, columns=["location", "lat", "lon", "confirmed"])
            

            #Readable values
            confirmed_source["confirmed_readable"] = confirmed_source["confirmed"].apply(human_format)
            display_confirmed_source = pd.DataFrame(confirmed_source, columns=["location", "lat", "lon", "confirmed_readable"]).reset_index(drop=True)
            display_confirmed_source = display_confirmed_source.rename(columns={"confirmed_readable": "confirmed"})
            st.dataframe(display_confirmed_source)

            INITIAL_VIEW_STATE = pdk.ViewState(
                latitude=55.3781,
                longitude=-3.436,
                zoom=1,
                pitch=25,
            )

            column_layer = pdk.Layer(
                "ColumnLayer",
                data=confirmed_source,
                get_position=["lon", "lat"],
                radius=50000,
                get_elevation="confirmed",
                elevation_scale=0.25,
                get_fill_color=["255,255, confirmed*.01"],
                get_line_color=[255, 255, 255],
                filled=True,
                pickable=True,
                extruded=True,
                auto_highlight=True,
            )
            TOOLTIP = {
                "html": "{location}<br> <b>{confirmed_readable}</b> Confirmed Cases",
                "style": {
                    "background": "grey",
                    "color": "white",
                    "font-family": '"Helvetica Neue", Arial',
                    "z-index": "10000",
                },
            }

            r = pdk.Deck(
                column_layer,
                map_style="mapbox://styles/mapbox/satellite-streets-v11",
                map_provider="mapbox",
                initial_view_state=INITIAL_VIEW_STATE,
                tooltip=TOOLTIP,
            )
            st.write("## Total Number of Confirmed Cases All Time")
            st.pydeck_chart(r)
    else:
        st.write("Select Valid Dates to continue")


if __name__ == "__main__":
    main()
