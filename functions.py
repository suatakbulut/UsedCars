# test
import pandas as pd
import requests
from bs4 import BeautifulSoup 
import dill 
from PIL import Image
import os 
import altair as alt 
from datetime import datetime 
from itertools import product
import chart_studio.tools as tls
import chart_studio.plotly as py
import plotly.graph_objects as go 
import numpy as np

class Model:
	def __init__(self, model_path='static/model.dill'):
		self.model = dill.load(open(model_path, 'rb')) 

class Car:
	def __init__(self, car_data):
		self.state = car_data['state'][0]
		self.year = car_data['year'][0]
		self.manufacturer = car_data['manufacturer'][0]
		self.model = car_data['model'][0]
		self.odometer = car_data['odometer'][0]
		self.transmission = car_data['transmission'][0]
		self.condition = car_data['condition'][0]
		self.BaseMSRP = car_data['BaseMSRP'][0]
		self.df = pd.DataFrame.from_dict(car_data) 

	def fullName(self):
		return '-'.join([str(self.year), self.manufacturer, self.model]) 

	def titleName(self):
		return ' '.join([str(self.year), self.manufacturer.capitalize(), self.model.capitalize()]) 

	def complaints(self, numComplaints=6):
		try:
			url = f'https://www.carcomplaints.com/{self.manufacturer}/{self.model}/{self.year}/' 
			headers={'User-Agent': 'Mozilla/5.0'} 
			response = requests.get(url, headers=headers) 
			urlSoup = BeautifulSoup(response.content, "lxml")        
			container = urlSoup.find("div", attrs={"id":"graph"})
			complaints_list = container.ul.findAll('li')
			return [complaints_list[ind].strong.text.capitalize() for ind in range( min(len(complaints_list), numComplaints) )]

		except:
			print('Could not retreive complaints. . Error with Car.complaints() method.')
			return ['No mechanical issues retrieved']
			
	def price(self, Model):
		return int(Model.model.predict(self.df)[0])

	def reviews(self):
		try:
			model = self.model.replace('-', '_')
			model = model.replace(' ', '_')
			car = '-'.join([self.manufacturer, model, str(self.year)])
			url = f'https://www.cars.com/research/{car}/consumer-reviews/' 
			headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}         
			response = requests.get(url, headers=headers) 
			urlSoup = BeautifulSoup(response.content, "lxml")        
			
			container = urlSoup.find("div", attrs={"class":"review-header-details"})
			reviews = {} 

			overall = container.find('div', attrs={'class' : 'review-overall-stars'} )
			reviews['overall'] = { 
				'score': overall.p.text, 
				'num_reviews': overall.span.text}

			recommendation = container.find('div', attrs={'class' : 'rcmd-rate'} )
			reviews['recommendation_rate'] = recommendation.strong.text
			
			details_table = container.find('table', attrs={'class' : 'review-overall-averages'} )
			details_rows = details_table.findAll('tr')
			details = {}
			for details_row in details_rows:
				score, feature = details_row.text.replace('\n', '').split(' out of 5 stars')
				details[feature] = score
			reviews['details'] = details 

			return reviews 
			
		except:
			print('Could not retreive any reviews. . Error with Car.reviews() method.')
			reviews = {
				'details' : [], 
				'recommendation_rate' : None, 
				'overall' : {'score': None, 'num_reviews': None} 
				}
			return reviews

	def pic(self, car_img_dir='static'):
		try:
			url = f"https://www.newcartestdrive.com/reviews/{self.fullName()}/"
			response = requests.get(url)
			urlSoup = BeautifulSoup(response.content, "html.parser")
			img_div = urlSoup.find("div", attrs={"id":"thumb-box"})
			img_url = img_div.img.attrs['src'] 
			img = Image.open(requests.get(img_url, stream = True).raw) 
			file_path = os.path.join(car_img_dir, 'car_img.jpg')
			img.save(file_path)    
			return f"{self.fullName()}'s pic is successfully scraped"
		except:
			print('Could not retreive the image. Error with Car.pic() method.')
			pass

	def barChart(self, Model):	
		years = range( self.year-2, min(self.year+3, datetime.now().year+1) )
		conditions = ('fair', 'good', 'excellent', 'like new')
		df = pd.DataFrame( list(product(years, conditions)) , columns = ['year', 'condition'])
		for col in set(self.df.columns).difference(set(df.columns)):
			df[col] = self.df[col][0]
		cols = ['state', 'year', 'manufacturer', 'model', 'odometer', 'transmission', 'condition', 'BaseMSRP']
		df = df[cols]
		df['price'] = Model.model.predict(df) 
		barChart = alt.Chart(df).mark_bar().encode( 
			x=alt.X('condition:O', sort=['fair', 'good', 'excellent', 'like new']),
			y='price:Q',
			color=alt.Color('condition:O', sort=['fair', 'good', 'excellent', 'like new'], scale=alt.Scale(scheme='purplegreen')),
			column='year:N').properties(
				height = 240,
				width = 140,  
				padding = 10, 
				autosize=alt.AutoSizeParams(
				type = 'fit',
				contains = 'padding'
				) )

		#return barChart.to_json(indent=None).encode('utf-8') 
		return barChart.to_json(indent=None) 

	def map(self, Model):
		username = 'suatakbulut'
		api_key = 'OmWwvBMIO3rYLry5fn5F'
		tls.set_credentials_file(username=username, api_key=api_key)

		states = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'dc', 'de', 'fl', 
				'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 
				'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 
				'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 
				'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy']
		locations = [state.upper() for state in states]
		
		df = self.df.copy() 
		df = df.loc[df.index.repeat(len(states))].reset_index(drop = True) 
		df['state'] = states 
		preds = Model.model.predict(df) 
		predictions = [int(pred) for pred in preds]

		fig = go.Figure(data=go.Choropleth(
			locations=locations, # Spatial coordinates
			z = predictions, # Data to be color-coded
			locationmode = 'USA-states', # set of locations match entries in `locations`
			colorscale = 'PRGn',
			colorbar_title = "Thousands USD",
		))

		fig.update_layout(
			title_text = f'Used {self.titleName()} in {self.condition.capitalize()} Condition Prices by State',
			geo_scope='usa', # limite map scope to USA
		)

		return py.plot(fig, filename = 'usedCars_map', auto_open=False) 

if __name__ == '__main__': 
	car_data_1 = {
		'state' : ['al'], 
		'year' : [2014], 
		'manufacturer' : ['hyundai'], 
		'model' : ['sonata'], 
		'odometer' : [93600], 
		'transmission' : ['automatic'], 
		'condition' : ['excellent'], 
		'BaseMSRP' : [0]
		} 

	car_data_2 = {
		'state' : ['al'], 
		'year' : [2016], 
		'manufacturer' : ['mazda'], 
		'model' : ['cx-5'], 
		'odometer' : [54000], 
		'transmission' : ['automatic'], 
		'condition' : ['good'], 
		'BaseMSRP' : [0]
		} 

	model = Model(model_path='static/model.dill')
	car1 = Car(car_data_1)
	car2 = Car(car_data_2)

	testAll = True   
    
	if testAll:
		print('\nTesting fullName.')
		print(car1.fullName())
		print(car2.fullName())
		print('=================')

		print('\nTesting titleName.')
		print(car1.titleName())
		print(car2.titleName())
		print('=================')

		print('\nTesting complaints.')
		print(f'{car1.titleName()} : {car1.complaints()}') 
		print(f'{car2.titleName()} : {car2.complaints()}')
		print('=================')

		print('\nTesting price.')
		print(f'{car1.titleName()} : {car1.price(model)}') 
		print(f'{car2.titleName()} : {car2.price(model)}')
		print('=================')

		print('\nTesting reviews.')
		print(f'{car1.titleName()} : {car1.reviews()}') 
		print(f'{car2.titleName()} : {car2.reviews()}')
		print('=================')

		print('\nTesting pic.')
		print(f'{car1.titleName()} : {car1.pic()}') 
		print(f'{car2.titleName()} : {car2.pic()}')
		print('=================')

		print('\nTesting barChart.')
		print(f'{car1.titleName()} : {car1.barChart(model)}') 
		print(f'{car2.titleName()} : {car2.barChart(model)}')
		print('=================')	

		print('\nTesting map.')
		print(f'{car1.titleName()} : {car1.map(model)}') 
		print(f'{car2.titleName()} : {car2.map(model)}')
		print('=================')	

