import pandas as pd
import matplotlib.pyplot as plt
import datetime
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP
from pvlib.pvsystem import PVSystem, retrieve_sam
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.modelchain import ModelChain
import psycopg2
import psycopg2.extras
import json
import os


def get_connection():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.abspath(os.path.join(script_directory, '../../../'))
    file_path = os.path.join(target_directory, "db_credentials.json")
    db = json.load(open(file_path))
    return psycopg2.connect(user = db["user"],
                     password = db["password"],
                     host = db["host"],
                     port = db["port"],
                     database = db["database"]
                     )

latitudeEsfahan, longitudeEsfahan, tzEsfahan = 51.68, 32.65, 'Etc/GMT+4'

# specify time range and location.
start = pd.Timestamp(datetime.date.today()-pd.Timedelta(days=4), tz=tzEsfahan)
end = start + pd.Timedelta(days=7)
#Diffuse Horizontal Irradiance (DHI), Global Horizontal Irradiance (GHI), Direct Normal Irradiance (DNI)
irrad_vars = ['ghi', 'dni', 'dhi']

#preset pv modules parameters
sandia_modules = retrieve_sam('sandiamod')
#preset inverter parameters
cec_inverters = retrieve_sam('cecinverter')

module = sandia_modules['BP_Solar_BP3220N_Module___2010_'] #220W
myModule = module.copy()
#Values taken from retool panelPower
myModule["Voco"] = 36.5
myModule["Isco"] = 9.42 
myModule["Vmpo"] = 32.6
myModule["Impo"] = 8.42

inverter = cec_inverters['SMA_America__SC630CP_US__with_ABB_EcoDry_Ultra_transformer_']

temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']

system = PVSystem(surface_tilt=20, surface_azimuth=180, module_parameters=myModule, inverter_parameters=inverter, temperature_model_parameters=temperature_model_parameters, modules_per_string=25, strings_per_inverter=8)

fx_model = GFS()

fx_data = fx_model.get_processed_data(latitudeEsfahan, longitudeEsfahan, start, end)
fx_data = fx_data.resample('60min').interpolate()


mc = ModelChain(system, fx_model.location)
mc.run_model(fx_data)

data = (mc.results.ac.fillna(0)/200/274)
data = list(zip(data,data.index))

conn = get_connection()
cur = conn.cursor()
query = """INSERT INTO production.power_forecast (power_factor, time_stamp) VALUES (%s, %s)
ON CONFLICT (time_stamp) DO UPDATE
SET power_factor = EXCLUDED.power_factor
"""
psycopg2.extras.execute_batch(cur, query, data)
conn.commit()
conn.close()
print("data uploaded to db")