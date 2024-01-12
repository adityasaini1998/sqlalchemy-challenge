# Import necessary libraries
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
from functools import wraps

# Database Configuration and ORM Setup
def init_db_engine():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    return engine, Base.classes

db_engine, classes = init_db_engine()
Measurement, Station = classes.measurement, classes.station

# Session Management Decorator
def with_session(engine):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            with Session(engine) as session:
                return f(session, *args, **kwargs)
        return decorated_function
    return decorator

# Flask Application Initialization
app = Flask(__name__)

# API Route Definitions
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Endpoints:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>Format for 'start' and 'end' dates: MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
@with_session(db_engine)
def get_precipitation(session):
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    precipitation_dict = {date: prcp for date, prcp in precip_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
@with_session(db_engine)
def get_stations(session):
    station_data = session.query(Station.station).all()
    station_list = [station[0] for station in station_data]
    return jsonify(stations=station_list)

@app.route("/api/v1.0/tobs")
@with_session(db_engine)
def get_temperature_observations(session):
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_data = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= query_date).all()
    temperatures = [temp[0] for temp in temp_data]
    return jsonify(temperatures=temperatures)

@app.route("/api/v1.0/temp/<start>", defaults={'end': None})
@app.route("/api/v1.0/temp/<start>/<end>")
@with_session(db_engine)
def get_temp_stats(session, start, end):
    select_statement = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_date = dt.datetime.strptime(start, "%m%d%Y")
    
    if not end:
        results = session.query(*select_statement).filter(Measurement.date >= start_date).all()
        return jsonify([np.ravel(results)])

    end_date = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*select_statement).filter(Measurement.date.between(start_date, end_date)).all()
    return jsonify([np.ravel(results)])

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
