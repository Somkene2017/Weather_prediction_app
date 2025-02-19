# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 21:54:21 2023

@author: pc
"""


import numpy as np
import pickle
import sklearn
import json
import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import pytz

loaded_model = pickle.load(open("model_pack.json", 'rb'))

df = pd.read_csv("weather_forecast.csv")
'''
# Welcome!!!
'''
def weather_prediction(input_data):
    input_data_arr = np.asarray(input_data).reshape(1, -1)
    prediction = loaded_model.predict(input_data_arr)
    if prediction[0] == 0:
        return 'Rainy day'
    else:
        return 'Sunny day'

def main():
    st.title('Weather Prediction app')
    #left_column, right_column = st.columns(2)
    #left_column.radio('Outcome', np.unique(df.weather))
    #OR
    #with left_column:
        #left_column.radio('Outcome', np.unique(df.weather))
    st.text_input("please enter your name: ", key='name')
    precipitation = st.slider('What is the precipitation level:', 0.0, max(df['precipitation']))
    temp_max = st.slider('What is the maximum temperature (deg celcius)?: ', 0.0, max(df.temp_max))
    temp_min = st.slider('What is the minimum temperature (deg celcius)?; ', 0.0, max(df.temp_min))
    wind = st.slider('What is the wind level?: ', 0.0, max(df.wind))
    
    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_state(i):
        st.session_state.stage = i

    if st.session_state.stage == 0:
        weather_result = ''
        st.button('<-Weather prediction result->', on_click=set_state, args=[1])

    if st.session_state.stage >= 1:
        #name = st.text_input('Name', on_change=set_state, args=[2])
        weather_result = weather_prediction([precipitation, temp_max, temp_min, wind])
        st.success(weather_result)
        #st.write(f'Hello {name}!')
        time_var = ''
        time_var = pytz.timezone('Africa/Lagos').localize(datetime.now())
        time_value = time_var.strftime('%d/%m/%Y %H:%M:%S')
        correct_val = st.selectbox('What is the right value? ', [None, 'rain', 'sun'], on_change=set_state, args=[2])
        if correct_val is None:
            set_state(1)
    if (st.session_state.stage >= 2):
        #st.write(f':{color}[Thank you!]')
        new_data = [precipitation, temp_max, temp_min, wind, correct_val, time_value, st.session_state.name]
        df2 = pd.DataFrame([new_data])

        sheet_id = st.secrets.sheet_id
        worksheet_name = st.secrets.worksheet_name
        # Create a Google Sheet client
        credentials_dict = st.secrets["cred"]
        gc = gspread.service_account_from_dict(credentials_dict)
        # Open the Google Sheet
        sh = gc.open_by_key(sheet_id)

        # Get the worksheet
        ws = sh.worksheet(worksheet_name)

        # Append the DataFrame to the worksheet
        ws.append_rows(df2.values.tolist(), value_input_option='USER_ENTERED')
        f"Thank you {st.session_state.name} for your feedback. Click on 'Start Over' for another prediction"

        st.button('Start Over', on_click=set_state, args=[0])
        
if __name__ == '__main__':
    main()
