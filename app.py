import datetime as dt
import numpy as np
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Aloha! This API has available Hawaii weather data<br/>"
        f"Here are the available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of stations: /api/v1.0/stations<br/>"
        f"One year temperature observations: /api/v1.0/tobs<br/>"
        f"Temperature stats from start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stats from start to end date: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Query the average precipitation data by date
    sel = [Measurement.date, func.avg(Measurement.prcp)]
    results = session.query(*sel).\
        group_by(Measurement.date).all()

    # Terminate session
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    l = []   
    for date,prcp in results:
        d = {}
        d["Date"] = date
        d["Precipitation"] = prcp
        l.append(d)

    # Convert list to a JSON object and return
    return jsonify(l)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query the station data
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*sel).all()

    # Terminate session
    session.close()

    # Add the station names to a list
    l = []
    for station, name, latitude, longitude, elevation in results:
        d = {}
        d["Station"] = station
        d["Name"] = name
        d["Latitude"] = latitude
        d["Longitude"] = longitude
        d["Elevation"] = elevation
        l.append(d) 

    # Convert list to a JSON object and return
    return jsonify(l)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query the most recent date 
    recent_date = session.query(Measurement.date).\
        filter(Measurement.station == 'USC00519281').order_by(Measurement.date.desc()).\
        first()[0]
    # Convert to datetime
    y,m,d= recent_date.split('-')
    dt_converted = dt.datetime(int(y), int(m), int(d))

    # Compute the first day to query from
    dt_query = dt.date(dt_converted.year-1 , dt_converted.month, dt_converted.day+1)

    # Query temperature data after the dt_query date for the most active station
    sel = [Measurement.date,Measurement.tobs]
    results = session.query(*sel).\
        filter(Measurement.date>=dt_query).\
        filter(Measurement.station == 'USC00519281').\
        group_by(Measurement.date).all()

    # Terminate session
    session.close()

    l = []
    for date, tobs in results:
        d = {}
        d["Date"] = date
        d["Temperature"] = tobs
        l.append(d)

    # Convert list to a JSON object and return
    return jsonify(l)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    # Query min, max, and average values since the given start date
    sel =[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    results = session.query(*sel).\
        filter(Measurement.date >= start).all()
    # Terminate session
    session.close()
    
    l = []
    for min_temp, avg_temp, max_temp in results:
        d = {}
        d["Min"] = min_temp
        d["Average"] = avg_temp
        d["Max"] = max_temp
        l.append(d)

    # Convert list to a JSON object and return
    return jsonify(l)

@app.route("/api/v1.0/<start>/<end>")
def end(start,end):
    session = Session(engine)

    # Query min, max, and average values between the given start and end date
    sel =[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    l = []
    for min_temp, avg_temp, max_temp in results:
        d = {}
        d["Min"] = min_temp
        d["Average"] = avg_temp
        d["Max"] = max_temp
        l.append(d)

    # Convert list to a JSON object and return
    return jsonify(l)

if __name__ == "__main__":
    app.run(debug=True)