# Import the dependencies.
import numpy as np
import datetime
import sqlalchemy 
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
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)   **Not going to use this here**

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all the available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve only the last 12 months of data."""
    session = Session(engine)

    one_year_ago = datetime.date(2016, 8, 24)  

    # Query for the last year of data from one_year_ago
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)



@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    
    all_stations = session.query(Station.station,Station.name).all()

    session.close() 

    station_info = []
    for station, id in all_stations:
        station_info_dict = {}
        station_info_dict['station'] = station
        station_info_dict['id'] = id
        station_info.append(station_info_dict)

    return jsonify (station_info) 


@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    session = Session(engine)

    #most_active = session.query

     # Query to find most active station
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate date 1 year ago from end of data
    query_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = datetime.datetime.strptime(query_date, '%Y-%m-%d') - datetime.timedelta(days=365)
    # Query temp observations for most active station for previous year 
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == active_station).\
                filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Create JSON list 
    temps = []
    for date, temp in results:
        temps.append({"date": date, "temperature": temp})
        
    return jsonify(temps)


@app.route("/api/v1.0/<start>")
def temp_start(start):

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    session = Session(engine)

    one_year_ago = datetime.date(2016, 8, 24)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= one_year_ago).all()

    session.close()

    temps = []
    for min,avg,max in results:
        temps_dict = {}
        temps_dict["TMIN"] = min
        temps_dict["TAVG"] = avg
        temps_dict["TMAX"] = max
        temps.append(temps_dict)
        
    return jsonify(temps)

###############################################################

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):

    session = Session(engine)

    start_date = datetime.date(start, 2016, 8, 24)
    end_date = datetime.date(start, 2017, 8, 23)

    results = session.query(Measurement.date,
                func.min(Measurement.tobs), 
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).\
            group_by(Measurement.date).all()
                   

    session.close()
    
    temps_start_end = []
    for date, min, avg, max in results:
        temps_se_dict = {}
        temps_se_dict["Date"] = date
        temps_se_dict["TMIN"] = min
        temps_se_dict["TAVG"] = avg
        temps_se_dict["TMAX"] = max
        temps_start_end.append(temps_se_dict)
        
    return jsonify(temps_start_end)






if __name__ == '__main__':
    app.run(debug=True)