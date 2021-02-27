from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

first_row = session.query(Measurement).first()
first_row.__dict__

first_row = session.query(Station).first()
first_row.__dict__

for row in session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).limit(15).all():
    print(row)

for row in session.query(Measurement.id, Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs).order_by(Measurement.date.desc()).limit(15).all():
    print(row)

last_date = dt.datetime(2017, 8, 23)
one_year_date = last_date - dt.timedelta(days=365)
print("Last 12 Months: ", one_year_date)

results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_date).all()
for result in results:
    print(f"Date: {result.date}, Precipitation: {result.prcp}")

df = pd.DataFrame(results, columns=['date', 'precipitation'])
df.set_index('date', inplace=True, )
# Sort the dataframe by date
df=df.sort_index()
df

df.plot(rot=90, legend=False)
plt.yticks(np.arange(0, 7, step=0.5))
plt.title('Precipitation')
plt.ylabel('Inches')
plt.xlabel('Date')
plt.figure(figsize=(6, 6))
plt.show()

df.describe()

inspector = inspect(engine)
columns = inspector.get_columns('measurement')
for c in columns:
    print(c['name'], c["type"])

station_table=session.query(func.count(Station.station)).all()
station_table

sel = [Measurement.station, 
       func.count(Measurement.station)
      ]
station_count = session.query(*sel).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
station_count

sel = [Measurement.station, 
       func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs) 
       ]
station_temp = session.query(*sel).\
    filter(Measurement.station == "USC00519281").all()
station_temp

date1 = dt.datetime(2016, 8, 23)

sel = [Measurement.station, 
       func.count(Measurement.station) 
      ]
year_temp = session.query(*sel).\
    filter(Measurement.date >= date1).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
year_temp

sel = [Measurement.date, Measurement.tobs]
temp_year = session.query(*sel).\
    filter(Measurement.date >= one_year_date).filter(Measurement.station == "USC00519281").all()
#temp_year

temp_year_df = pd.DataFrame(temp_year, columns=['date', 'tobs'])
temp_year_df.set_index('date', inplace=True, )
# Sort the dataframe by date
temp_year_df=temp_year_df.sort_index()
#temp_year_df

ax = temp_year_df.plot.hist(bins=12, alpha=0.5)

inspector = inspect(engine)
inspector.get_table_names()

columns = inspector.get_columns('measurement')
for c in columns:
    print(c['name'], c["type"])

columns = inspector.get_columns('station')
for c in columns:
    print(c['name'], c["type"])

session.query(Measurement.station, Station.station).limit(10).all()

same_station = session.query(Measurement, Station).filter(Measurement.station == Station.station).limit(10).all()

for record in same_station:
    (measurement, station) = record
    print(measurement.station)
    print(station.station)

sel = [Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs, Station.latitude, Station.longitude, Station.elevation]
same_station = session.query(*sel).filter(Measurement.station == Station.station).limit(10).all()

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation by date """
    # Query all 
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
# Create a dictionary from the row data and append to a list of all_points
    all_points = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_points.append(precipitation_dict)

    return jsonify(all_points)

@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all 
    results = session.query(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperatures():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data for last year"""
    # Query all 
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_date).all()

    session.close()

    all_temperatures = list(np.ravel(results))

    return jsonify(all_temperatures)

    
if __name__ == '__main__':
    app.run(debug=True)