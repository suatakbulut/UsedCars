from flask import Flask, render_template, request
from functions import Model, Car 
from Alltogether import GroupbyEstimator, estimator_factory
from ScrapeTools import scrape_NewCarsTestDrive, extract_msrp
import os 
import numpy as np

app = Flask(__name__) 
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 
# model_path = 'forest_model.dill'
model_path = 'static/model.dill'
@app.route('/')
def root(): 
	return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
	try: 
		year = int(request.form['year'].strip())
		manufacturer = request.form['manufacturer'].strip().lower()
		model = request.form['model'].strip().lower()
		odometer = int(request.form['odometer'].strip())
		state = request.form['state'].strip().lower()
		transmission = request.form['transmission']
		condition = ' '.join(request.form['condition'].split('_'))

		temp_name = '-'.join([str(year), manufacturer, model])
		msrp = scrape_NewCarsTestDrive(temp_name)
		if msrp:
			msrp = int(msrp.split(',')[1][:-1])
		else:
			msrp = 26294
		
		car_data = {
			'state' : [state], 
			'year' : [year], 
			'manufacturer' : [manufacturer], 
			'model' : [model], 
			'odometer' : [odometer], 
			'transmission' : [transmission], 
			'condition' : [condition], 
			'BaseMSRP' : [msrp]
			} 
		
		car = Car(car_data)
		reviews = car.reviews() 
		model = Model(model_path = model_path) 
		map_reference = car.map(model) 
		barChart = car.barChart(model) 
		price = car.price(model) 
		car.pic() 
		car_name = car.titleName() 
		complaints = car.complaints() 
		
		return render_template(
			'response.txt', 
			CarName = car_name, 
			complaints=complaints, 
			reviews=reviews, 
			condition=condition, 
			price=price, 
			barChart_spec = barChart,
			map_reference = map_reference)    
	
	except:
		message = 'Please enter valid values.'
		return render_template('index.html', message = message) 

@app.route('/home')
def home():
  return render_template('index.html')

@app.after_request
def add_header(response):
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response

if __name__ == '__main__':
	app.debug = True
	app.run()
