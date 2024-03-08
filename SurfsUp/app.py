# Import the dependencies.

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

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
session = Session(engine)

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"api/v1.0/<start><br/>"
        f"api/v1.0/<start>/<end><br/>"
    )
@app.route("/api/v1.0/precipitation")
def precip():

    last_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_string = last_date_str[0]
    list = last_date_string.split('-')
    y = int(list[0])
    m = int(list[1])
    d = int(list[2])
    year_before = dt.date(y, m ,d)-dt.timedelta(days=365)
    one_year = session.query(Measurement.id, Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs).\
    filter(Measurement.date>= year_before).\
        order_by(Measurement.date).all()
    
    session.close()

    one_year_df = pd.DataFrame(one_year, columns = ['id', 'Station', 'Date', "Precipitation", 'Obs Temp'])
    precip_dict = one_year_df.set_index('Date')['Precipitation'].to_dict()
    return jsonify(precip_dict)
################################
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    sel = [Station.station, func.count(Station.station)]
    id_vals = session.query(*sel).group_by(Station.station).all()
    id_vals

    ids = []
    for i in id_vals:
        ids.append(i[0])

    session.close()

    return jsonify(ids)

########################################

@app.route("/api/v1.0/tobs")
def temps():

    session = Session(engine)
    # finds the most recent date in the data
    #last_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #last_date_string = last_date_str[0]
    #split the string into Year - month - day variables, identifying the dash as the separating character in the string. transform into integers
    #list = last_date_string.split('-')
    #y = int(list[0])
    #m = int(list[1])
    #d = int(list[2])
    #get the date one year before the most recent date in the data
    # I resorted to entering the year, month, and day as my code looked like it worked in Jupyter notebook but errored here
    year_before = dt.date(2017,8,23)-dt.timedelta(days=365)

    #this code gets the most active station
    #results = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        #order_by(func.count(Measurement.station).desc()).first()

    # my code looked like it was working but I was getting an error - I resorted to entering the most active station.
    most_active = "USC00519281"

    # getting the date and temp for the last 12 months for the most active station
    active_year = session.query(Measurement.tobs).\
    filter(Measurement.station == most_active).filter(Measurement.date>= year_before).all()
    
    session.close()
    result = list(np.ravel(active_year))
    return jsonify(temps=result)

######################################

@app.route("/api/v1.0/temp_min_max_avg/<startdate>")
def temp_min_max_avg_date(startdate):

####In this section, I think I still need to decipher what is being requested.

    session = Session(engine)

   #  code to request and get start date as y,m,d
    #y = int(input("Enter the year (yyyy) for your desired start date:"))
    #m = int(input("Enter the month (mm) for your desired start date:"))
    #d = int(input("Enter the day (dd) for your desired start date:"))

    #start_date = dt.date(startdate)

    #results = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        #rder_by(func.count(Measurement.station).desc()).first()

    # my code looked like it was working but I was getting an error - I resorted to entering the most active station.
    most_active = "USC00519281"

  # getting the date and temp for the most active station for all dates after the provided start date
    #start_temps = session.query(Measurement.date, Measurement.tobs).\
    #filter(Measurement.date>= start_date).\
        #order_by(Measurement.date).all()

  # getting the min, max, and average for the period after the specified date
    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    temps = session.query(*sel).\
       filter(Measurement.station == most_active).filter(Measurement.date>= startdate).all()

    session.close()
    result = list(np.ravel(temps))
    return jsonify(result)

##################################################

@app.route("/api/v1.0/range/<start_date>/<end_date>", methods=['GET'])
def get_range(start_date, end_date):

    session = Session(engine)

    #results = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
       # order_by(func.count(Measurement.station).desc()).first()

    most_active = "USC00519281"

  # getting the date and temp for the most active station for all dates in the specified date range
    #period_temps = session.query(Measurement.date, Measurement.tobs).\
    #filter(Measurement.date>= start_date, Measurement.date<= end_date, Measurement.station == most_active).\
        #order_by(Measurement.date).all()
    
  # getting the min, max, and average for the specified period  
    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    temps = session.query(*sel).\
       filter(Measurement.station == most_active).filter(Measurement.date>= start_date).filter(Measurement.date<= end_date).all()
    
    temps
    result = list(np.ravel(temps))
    session.close()

    return jsonify(temps)


###########################
if __name__ == "__main__":
    app.run(debug=True)