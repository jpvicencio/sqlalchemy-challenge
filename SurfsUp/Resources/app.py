import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine)
 

# Save references to each table
ST = Base.classes.station  
ME = Base.classes.measurement 
session = Session(engine)

# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        "Aloha!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(ME.date).order_by(ME.date.desc()).first()[0]
    query_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    date_precipitation = session.query(ME.date, ME.prcp).filter(ME.date >= query_date).all()
    precipitation_dict = {date: prcp for date, prcp in date_precipitation}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(ST.station).all()
    return jsonify([station[0] for station in stations_list])

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(ME.station).group_by(ME.station).order_by(func.count(ME.station).desc()).first()[0]
    most_recent_date = session.query(ME.date).order_by(ME.date.desc()).first()[0]
    query_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    temperature_data = session.query(ME.date, ME.tobs).filter(ME.station == most_active_station).filter(ME.date >= query_date).all()
    return jsonify([temp[1] for temp in temperature_data])

@app.route("/api/v1.0/<start>")
def start(start):
    results = session.query(func.min(ME.tobs), func.avg(ME.tobs), func.max(ME.tobs)).filter(ME.date >= start).all()
    return jsonify(list(results[0]))


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    results = session.query(func.min(ME.tobs), func.avg(ME.tobs), func.max(ME.tobs)).filter(ME.date >= start).filter(ME.date <= end).all()
    return jsonify(list(results[0]))

if __name__ == "__main__":
    app.run(debug=True)

