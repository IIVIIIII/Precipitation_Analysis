import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/*start*<br/>"
        f"/api/v1.0/*start*/*end*"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data including the ammount and date it was measured"""
    # Query all passengers

    year_before = dt.datetime.strptime(session.query(measurement.date).order_by(measurement.date.desc()).first()[0], '%Y-%m-%d').date() - dt.timedelta(days=365)
    that = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()[0][0]

    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= year_before).\
        filter(measurement.station == that).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precip_date
    date_precip = []
    for date, precip in results:
        precipitation = {}
        precipitation[date] = precip
        date_precip.append(precipitation)

    return jsonify(date_precip)



@app.route("/api/v1.0/stations")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data from most active station in the most recent year avaliable including the ammount and date it was measured"""

    # Query all relevant precipitation and dates
    year_before = dt.datetime.strptime(session.query(measurement.date).order_by(measurement.date.desc()).first()[0], '%Y-%m-%d').date() - dt.timedelta(days=365)
    that = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()[0][0]

    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= year_before).\
        filter(measurement.station == that).all()

    session.close()

    return jsonify(list(results))



@app.route("/api/v1.0/<start>")
def temp_sum_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Get precipitation data since the date indicated"""

    start_date = start

    results = session.query(func.max(measurement.tobs), func.min(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

    session.close()

    return jsonify(list(np.ravel(results)))



@app.route("/api/v1.0/<start>/<end>")
def temp_sum_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Get precipitation within the time range of the dates indicated"""

    start_date = start
    end_date = end

    results = session.query(func.max(measurement.tobs), func.min(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).all()

    session.close()

    return jsonify(list(np.ravel(results)))



if __name__ == '__main__':
    app.run(debug=True)