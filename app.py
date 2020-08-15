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

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date,func.avg(Measurement.prcp)).\
        group_by(Measurement.date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    d = {}    
    for result in results:
        d[result[0]] = result[1]

    return jsonify(d)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station,Station.name)

    stations = [result[1] for result in results]
    
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(Measurement.date).\
    filter(Measurement.station == 'USC00519281').order_by(Measurement.date.desc()).\
    first()
    results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date<=recent_date[0]).\
        filter(Measurement.date>='2016-08-19').filter(Measurement.station == 'USC00519281').\
        group_by(Measurement.date).all()

    temp = [result[1] for result in results]
    
    return jsonify(temp)

@app.route("/api/v1.0/<start>/<end>")
def end_date(start,end):

    if end == "":
        result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        temps = [result[0][0],result[0][1],result[0][2]]
    else:
        result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = [result[0][0],result[0][1],result[0][2]]
    
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start_date(start):

    result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    temps = [result[0][0],result[0][1],result[0][2]]

    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)