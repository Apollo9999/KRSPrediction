## KRS Dam Water Storage prediction

This repository contains and showcases  the work performed  in developing a predictive model that estimates the reservoir water availability at least 1-3 months in advance using hydro-meteorological parameters and reservoir water level data for Wave2Web Hackathon. The main aim of this Hackathon is to develop a predictive model to forecast water availability in the select reservoir(s) supplying water in Bengaluru, India.

We have collected weather data, land use, water use to come up with a model based on historical water availability, hydro-meteorological data, and water demand. [This document](https://github.com/Arghyam-Team/KRSPrediction/blob/main/Arghyam%20Final%20Report.pdf) contains the complete details. 

We have trained several types of models using LSTM to forecast water availability for one day, 30 days, 60 days, and 90 days. The features considered for model training are Present storage in TMC, inflow, outflow, Maximum Temprature, visibility, humidity and wind. The details of the trained models are presented in the below table. 

<img src="https://github.com/Arghyam-Team/KRSPrediction/blob/main/Images/model%20summary.PNG" width="600" height="400">

The [prediction dashboard](http://65.2.75.233:8501/) is deployed in a free tier AWS EC2 instance using the python Streamlit library. The chatbot is developed in RASA V2.5 and deployed on Heroku. The actual client is running on a flask instance on the same AWS instance as the dashboard.

### Major Features
- Proposed water availability prediction model for 1 - 3 months (30 days to 90 days) using deep learning from weather and reservior data.
- Complex models introduced overfitting as training data is limited. Simpler models resulted good accuracy.
- Weather data alone is also sufficient to predict the water availability.

### Installation

* Clone the git repository
* Create a python virtual environment. We recommend Python 3.7 or 3.8
* Install the requirements after activating the virtual environment. `pip install -r requirements.txt`
* You need to run two things: The flask chatbot application `python flask_app/flask_main.py` and, the streamlit app `streamlit run app/main.py`.
* The RASA backend is already deployed on Heroku.
* For daily updates run `python dailyupdate.py`. Can be schedules as a cron job.

### Model details
The trained models are in the `models` folder. We trained lot more models in the experimentation stage before drilling down to the models that gave the best performance. `lstmtest.py` contains the code for training the models and `forecasting.py` contains code for running the predictions.

### References
- [Sources of Drinking water in Bangalore](https://www.karnataka.com/bangalore/what-is-the-source-of-drinking-water-in-bangalore/)
- [Operation and Maintenance Manual for Krishnarajasagara Dam](http://waterresources.kar.nic.in/KRS_OM_KaWRD.pdf)



