# Imports
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from shinywidgets import render_widget

# Import icons
from faicons import icon_svg

# Set a constant UPDATE INTERVAL for all live data
UPDATE_INTERVAL_SECS: int = 3

# Initialize reactive value, wrapper around deque
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# Initialize reactive calculation
@reactive.calc()
def reactive_calc_combined():

    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random between 45 and 51 C, rounded to 1 decimal place
    temp = round(random.uniform(65, 76), 1)

    # Get a timestamp for "now"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # Get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple everything we need
    return deque_snapshot, df, latest_dictionary_entry

# Define the Shiny UI Page layout, set the title
ui.page_opts(title="Weather in San Jose, CA", fillable=True)

# Define the UI Layout Sidebar with background color
with ui.sidebar(open="open", style="background-color: #f5f5f5"):
    
    # Header with two lines
    with ui.h2(class_="text-center"):
        ui.div("San Jose Weather", style="font-size: 1.0em;"),
        ui.div("Monitoring Dashboard", style="font-size: 1.0em;")
    
    # Description
    ui.p(
        "Real-time temperature readings in San Jose, CA",
        class_="text-center",
    )
    ui.hr() # Horizontal line for visual separation
    
    # Links section
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/SMStclair/cintel-05-cintel",
        target="_blank",
        style="color: #660066"
    )
    ui.a(
        "GitHub App",
        href="https://github.com/SMStclair/cintel-05-cintel/blob/main/dashboard/app.py",
        target="_blank",
        style="color: #660066"
    )
    ui.a(
        "PyShiny", 
        href="https://shiny.posit.co/py/", 
        target="_blank",
        style="color: #660066"
    )
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
        style="color: #660066"
    )
# Display current temperature in the main panel
with ui.layout_column_wrap(fill=False):
    # Display icon and title in the main panel
    with ui.value_box(
        title="San Jose Climate Monitoring Dashboard",
        showcase=icon_svg("sun"),
        value="",
    ):
        pass

    
    with ui.value_box(
        showcase=icon_svg("sun"),
    ):
        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} F"

    # Display current day and time card
    with ui.card(full_screen=True):
    # Customize card header with background color, text, and icon
        ui.card_header(
        "📅 Current Date and Time",
        style="background-color: blue; color: white;",
    )

        # Customize card content text color and font size
        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

        # Add icon
        icon_svg("clock")

with ui.layout_column_wrap(fill=False):
    
    # Display the DataFrame
    with ui.card(style="width: 100%; height: 200px;"):
        ui.card_header("📊 Readings Data Table", style="background-color: #e6e6fa; color: black;")

        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)        # Use maximum width
            return render.DataGrid( df,width="100%")
        
# Display the chart with current trend
with ui.layout_columns(col_widths=[12, 6]):
    with ui.card(full_screen=True):
        ui.card_header("Chart with Current Trend", style="background-color: #ff00ff; color: black;")

        # Initialize an empty figure
        fig = px.line(title="Temperature Trend Over Time", labels={"temp": "Temperature (°F)", "timestamp": "Time"})

        @render_plotly
        def display_plot():
            # Fetch data from the reactive calc function
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

            # Ensure the DataFrame is not empty before updating the plot
            if not df.empty:
                # Convert the 'timestamp' column to datetime for better plotting
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                # Add trace for temperature data
                fig.add_scatter(x=df["timestamp"], y=df["temp"], mode="lines", name="Temperature")

                # Configure animation settings
                fig.update_layout(updatemenus=[dict(type="buttons", showactive=False, buttons=[dict(label="Play", method="animate", args=[None, {"fromcurrent": True}]),])])

                # Update layout as needed to customize further
                fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°F)")

            return fig