import pandas as pd
import oAuth2 as token
import globalVariables as gv
import requests
import csv
import time
from datetime import datetime

"""

@author: Rohullah Najibi
Developed for reading and writing nest thermostat attributes

"""
 
"""
function to convert Celsius to Fahrenheit

Parameters
----------
t - int: temp in celsius


Returns
-------
temp in fahrenheit - int

"""
def convertCtoF(t):
    return (t * 9/5) + 32

"""
function to convert Fahrenheit to Celsius

Parameters
----------
t - int: temp in fahrenheit


Returns
-------
temp in celsius - int

"""
def convertFtoC(t):
    return (t - 32) * 5/9

"""
create a CSV file and specify the column names

Parameters
----------
filename - string
        name of the file to be created appended by .csv
columns - list of strings
        name of the columns of the csv


Returns
-------
none

"""
def create_csv(filename, columns):
    df = pd.DataFrame(columns=columns)
    df.to_csv(filename, index=False)
    
"""
append data to the CSV file

Parameters
----------
filename - string
        name of the file
data - list of strings
        values of the columns


Returns
-------
none

"""

def append_data_to_csv(filename, data):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(data)

"""
get the first value from the csv file

Parameters
----------
filename - string
        name of the file


Returns
-------
first value from the csv file - int

"""

def read_value_from_csv(filename):
    with open(filename, 'r') as file:
        # Create a CSV reader
        reader = csv.reader(file)

        # Read the first row
        row = next(reader)

        # Read the first cell value
        first_value = row[0]
        return first_value
    
"""

This function will read the specific data from the thermostat device and saves them to a csv file
This function does all attribute readings from the thermostat
Firstly, the access token is used to verify that the developer 
has the necessary permissions/credentials to make api calls. 
the api sends a response, which includes all the data the nest thermostat device has.
the following information is extracted:
It includes Timestamp, Device Name, Device Type, Localization, 
Connectivity, Ambient Temperature in Celsius, Ambient Temperature in Fahrenheit, 
Thermostat Mode, Thermostat Available Modes, Heat Target Temperature, 
Cool Target Temperature, Humidity, Fan, Thermostat Eco Mode, 
Thermostat Eco Heat in Celsius, Thermostat Eco Heat  in Fahrenheit, 
Thermostat Eco Cool Celsius,  Thermostat Eco Cool Fahrenheit, Thermostat HVAC
After data is extracted, they are placed on an array and written on a Google spreadsheet.


Parameters
----------
access_token - string
        name of the file


Returns
-------
none

"""
def read_API_data(access_token):
    url_get_devices = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + gv.project_id + '/devices'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token
    }
    response = requests.get(url_get_devices, headers=headers)
    response_body = response.json()
    now = datetime.now()
    
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    device_name = response_body['devices'][0]['name']
    device_type = response_body['devices'][0]['type']
    localization = 'Thermostat'
    connectivity = response_body['devices'][0]['traits']['sdm.devices.traits.Connectivity']['status']
    temp_celcius = response_body['devices'][0]['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
    temp_farenheit = convertCtoF(temp_celcius)
    thermostat_mode = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatMode']['mode']
    thermostat_available_modes = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatMode']['availableModes']
    heat_target_temp = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']['heatCelsius']
    # cool_target_temp does not exist now since not connected to a real system
    # cool_target_temp = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']['coolCelsius']
    cool_target_temp = ''
    humidity = response_body['devices'][0]['traits']['sdm.devices.traits.Humidity']['ambientHumidityPercent']
    # fan does not exist now since not connected to a real system
    # fan = response_body['devices'][0]['traits']['sdm.devices.traits.Fan']['timerMode']
    fan = ''
    thermostat_eco_mode = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatEco']['mode']
    thermostat_eco_heat_celcius = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatEco']['heatCelsius']
    thermostat_eco_heat_farenheit = convertCtoF(thermostat_eco_heat_celcius)
    thermostat_eco_cool_celcius = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatEco']['coolCelsius']
    thermostat_eco_cool_farenheit = convertCtoF(thermostat_eco_cool_celcius)
    thermostat_Hvac = response_body['devices'][0]['traits']['sdm.devices.traits.ThermostatHvac']['status']
    row = [time, device_name, device_type, localization, connectivity, temp_celcius, temp_farenheit, thermostat_mode,
           thermostat_available_modes, heat_target_temp, cool_target_temp, humidity, fan, thermostat_eco_mode,
           thermostat_eco_heat_celcius, thermostat_eco_cool_celcius, thermostat_eco_cool_farenheit, thermostat_Hvac]
    append_data_to_csv(file_name, row)
    

"""
This function sets the thermostat mode to heat

Parameters
----------
access_token - string


Returns
-------
- nothing if mode change is done successfully
- returns explanation if it errors

"""
def set_mode_to_heat(access_token):
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1' + '/enterprises/'  + gv.project_id + '/devices/' + gv.thermostat + ':executeCommand'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }

    data = '{ "command" : "sdm.devices.commands.ThermostatMode.SetMode", "params" : { "mode" : "HEAT" } }'

    response = requests.post(url_set_mode, headers=headers, data=data)

    print(response.json())

    

"""
This function sets the heating setpoint from the value it reads from the csv file
pre-condition to set target heat temperature is to set mode to heat; thus it calls
set_mode_to_heat() function

Parameters
----------
access_token - string


Returns
-------
- nothing if mode change is done successfully
- returns explanation if it errors

"""
def set_target_heat_temp(access_token):
    set_mode_to_heat(access_token)
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1/' + 'enterprises/'  + gv.project_id + '/devices/' + gv.thermostat + ':executeCommand'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    set_temp_to = read_value_from_csv('FDD.csv')
    data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", "params" : {"heatCelsius" : ' + str(set_temp_to) + '} }'

    response = requests.post(url_set_mode, headers=headers, data=data)

    print(response.json())


"""
This function sets the thermostat mode to cool

Parameters
----------
access_token - string


Returns
-------
- nothing if mode change is done successfully
- returns explanation if it errors

"""
def set_mode_to_cool(access_token):
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1' + '/enterprises/'  + gv.project_id + '/devices/' + gv.thermostat + ':executeCommand'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }

    data = '{ "command" : "sdm.devices.commands.ThermostatMode.SetMode", "params" : { "mode" : "COOL" } }'

    response = requests.post(url_set_mode, headers=headers, data=data)

    print(response.json())

  
"""
This function sets the heating setpoint from the value it reads from the csv file
pre-condition to set target heat temperature is to set mode to cool; thus it calls
set_mode_to_cool() function

Parameters
----------
access_token - string


Returns
-------
- nothing if mode change is done successfully
- returns explanation if it errors

"""  
def set_target_heat_cool(access_token):
    set_mode_to_cool(access_token)
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1/' + 'enterprises/'  + gv.project_id + '/devices/' + gv.thermostat + ':executeCommand'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    set_temp_to = read_value_from_csv('FDD.csv')
    data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetCool", "params" : {"coolCelsius" : ' + str(set_temp_to) + '} }'

    response = requests.post(url_set_mode, headers=headers, data=data)

    print(response.json())



"""
This function sets the thermostat mode to heatcool

Parameters
----------
access_token - string


Returns
-------
- nothing if mode change is done successfully
- returns explanation if it errors

"""
def set_mode_to_heat_cool(access_token):
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1' + '/enterprises/'  + gv.project_id + '/devices/' + gv.thermostat + ':executeCommand'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }

    data = '{ "command" : "sdm.devices.commands.ThermostatMode.SetMode", "params" : { "mode" : "HEATCOOL" } }'

    response = requests.post(url_set_mode, headers=headers, data=data)

    print(response.json())

    
"""
This function sets the heating setpoint from the value it reads from the csv file
pre-condition to set target heat temperature is to set mode to heatcool; thus it calls
set_mode_to_heat_cool() function

Parameters
----------
access_token - string


Returns
-------
- nothing if mode change is done successfully
- returns explanation if it errors

""" 
def set_target_heat_and_cool_temp(access_token):
    set_mode_to_heat_cool(access_token)
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1/' + 'enterprises/'  + gv.project_id + '/devices/' + gv.thermostat + ':executeCommand'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    set_heat = read_value_from_csv('FDD.csv')
    set_cool = 11 # dummy data
    data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetRange", "params" : {"heatCelsius" : ' + str(set_heat) + ', "coolCelsius" : ' + str(set_cool) + '} }'

    response = requests.post(url_set_mode, headers=headers, data=data)

    print(response.json())

file_name = "thermostat_readings.csv"
column_names = ['Timestamp', 'Device_Name', 'Device_Type', 'Localization',
                'Connectivity', 'Temp_Celsius', 'Temp_Fahrenheit', 'Thermostat_Mode',
                'Thermostat_Available_Modes', 'Heat_Target Temperature',
                'Cool_Target_Temperature', 'Humidity', 'Fan', 'Thermostat_Eco_Mode',
                'Thermostat_Eco_Heat_Celsius', 'Thermostat_Eco_Heat_Fahrenheit',
                'Thermostat_Eco_Cool_Celsius', 'Thermostat_Eco_Cool_Fahrenheit',
                'Thermostat_HVAC']


# create_csv(file_name, column_names)
# create_csv('FDD.csv', [30])
access_token = token.get_access_token(gv.project_id, gv.client_id, gv.client_secret, gv.redirect_uri, gv.email)
access_token = "Bearer " + access_token
read_API_data(access_token)

# 5 min == 300 seconds
duration = 300

# Get the current time
start_time = time.time()
pause_interval = 20

# Run the function for five minutes
while time.time() - start_time < duration:
    read_API_data(access_token)
    time.sleep(pause_interval)


access_token = token.get_access_token(gv.project_id, gv.client_id, gv.client_secret, gv.redirect_uri, gv.email)
access_token = "Bearer " + access_token
set_target_heat_temp(access_token)

