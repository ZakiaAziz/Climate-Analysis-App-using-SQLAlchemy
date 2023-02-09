
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine
import datetime as dt
from flask import Flask, jsonify
import numpy as np

#Database Setup

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement= Base.classes.measurement
station=Base.classes.station
# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start/<start><br>"
        f"/api/v1.0/StarttoEnd/<start>/<end><br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    result=session.query(Measurement.station).distinct().all()

    session.close()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(result))

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def temparature():
    session = Session(engine)
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    result= session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date>prev_year).filter(Measurement.station == 'USC00519281').all()
    
    session.close()
    
    # Dict with date as the key and prcp as the value
    temp_prev = []
    for date, station, tobs in result:
        temp = {}
        temp["date"] = date
        temp["station"] = station
        temp["tobs"] = tobs
        temp_prev.append(temp)
        
    return jsonify(temp_prev)


@app.route("/api/v1.0/start/<start>")
def start_date(start):
    """Fetch the start date that matches
       the path variable supplied by the user, or a 404 if not."""

    canonicalised = start.replace(" ", "").lower()
    session = Session(engine)
    #result=session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))
    min_temp = session.query(Measurement.station,func.min(Measurement.tobs)).filter(Measurement.date>=canonicalised).all()
    max_temp = session.query(Measurement.station,func.max(Measurement.tobs)).filter(Measurement.date>=canonicalised).all()
    avg_temp= session.query(Measurement.station,func.avg(Measurement.tobs)).filter(Measurement.date>=canonicalised).all()
    session.close()
    
    
    TMIN = {date: tobs for date, tobs in min_temp}
    TMAX = {date: tobs for date, tobs in max_temp}
    TAVG = {date: tobs for date, tobs in avg_temp}
    return jsonify(TMIN, TMAX,TAVG)


@app.route("/api/v1.0/StarttoEnd/<start>/<end>")
def starttoend(start,end):
    """Fetch the start date that matches
       the path variable supplied by the user, or a 404 if not."""

    canonicalised_start = start.replace(" ", "").lower()
    canonicalised_end = end.replace(" ", "").lower()
    session = Session(engine)
    #result=session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))
    min_temp = session.query(Measurement.station,func.min(Measurement.tobs)).filter(Measurement.date>=canonicalised_start).filter(Measurement.date<=canonicalised_end).all()
    max_temp = session.query(Measurement.station,func.max(Measurement.tobs)).filter(Measurement.date>=canonicalised_start).filter(Measurement.date<=canonicalised_end).all()
    avg_temp= session.query(Measurement.station,func.avg(Measurement.tobs)).filter(Measurement.date>=canonicalised_start).filter(Measurement.date<=canonicalised_end).all()
    session.close()
    
    
    TMIN = {date: tobs for date, tobs in min_temp}
    TMAX = {date: tobs for date, tobs in max_temp}
    TAVG = {date: tobs for date, tobs in avg_temp}
    return jsonify(TMIN, TMAX,TAVG)

if __name__ == '__main__':
    app.run(debug=True)
