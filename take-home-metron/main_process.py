"""
This project is to read the sample water data coming from the meters
and clean it up using pandas df and show them on the webpage home 
"""

import os
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

# path to sample data file (adjust for whichever environment you're running in)
DATA_PATH = os.path.join(app.root_path, "data", "meter_data_sample.csv")

def load_and_clean(path: str = DATA_PATH) -> pd.DataFrame:
    """Read the meter CSV and return a cleaned DataFrame.

    Steps performed:
    1. read CSV
    2. drop any rows where a required field is missing (Device ID, Device Type,
       Timestamp, Volume Unit, Volume) so that nulls cannot skew later
       aggregations.
    3. coerce the timestamp column to datetime and drop invalid timestamps.
    4. convert all volumes to litres (1 gallon = 3.78541 litres) and write the
       result to ``volume_liters``; round this column to two decimal places.
    5. update ``Volume Unit`` to "liters" and drop the original ``Volume``
       column since it is no longer needed.
    6. sort the DataFrame by ``Device Type``, ``Device ID`` and ``Timestamp``
       to make grouping/plotting simpler.
    """
    df = pd.read_csv(path)

    # remove rows with missing critical information
    df = df.dropna(subset=["Device ID", "Device Type", "Timestamp", "Volume Unit", "Volume"])

    # convert timestamp column and drop malformed entries
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"])

    # helper for unit conversion
    gallon_to_liter = 3.78541
    def _to_liters(row):
        unit = str(row.get("Volume Unit", "")).strip().lower()
        if "gallon" in unit:
            return row["Volume"] * gallon_to_liter
        if "liter" in unit:
            return row["Volume"]
        return pd.NA

    df["volume_liters"] = df.apply(_to_liters, axis=1)

    # after conversion drop any rows where conversion failed
    df = df.dropna(subset=["volume_liters"])

    # normalise fields
    df["volume_liters"] = df["volume_liters"].round(2)
    df["Volume Unit"] = "liters"

    df = df.drop(columns=["Volume"], errors="ignore")

    # final sort for consistency
    df = df.sort_values(["Device Type", "Device ID", "Timestamp"])
    return df


@app.route('/')
def home():
    # load & clean data
    df = load_and_clean()

    # drop any remaining rows with nulls before rendering
    df = df.dropna()

    # render a preview table (limit so we don't bloat the page)
    # the original `Volume` column has been removed by load_and_clean
    table_html = (
        df.head(50)
        .to_html(classes="table table-striped", index=False, border=0, justify="center")
    )

    # prepare chart data grouped by device type/id
    chart_data = {}
    for (dtype, did), group in df.groupby(["Device Type", "Device ID"]):
        grp = group.sort_values("Timestamp")
        key = f"{dtype}:{did}"
        chart_data[key] = {
            "timestamps": grp["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
            "volumes": grp["volume_liters"].tolist(),
        }

    return render_template("home.html", table_html=table_html, chart_data=chart_data)


if __name__ == '__main__':
    app.run(debug=True)