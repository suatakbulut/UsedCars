It is always a huge hassle to decide when looking for a used car. There are so many options to consider. When doing a market research, people usually research the owner reviews, common technical issues, and local price of a spcific car. They might end up comparing it with other years or conditions of the same car as well as its price in neighbors for a better informed decision. 

This project aims to guide people in their search for a used car. It asks the potential buyer a few details about the car that they are interested in: make, model, year, odometer, condition, transmission, and state, and returns the following in a newat and compact way:

  - a picture of the car, 
  - the summary of owner reviews, 
  - the most 6 common technical issues reported by the owners, 
  - a bar-chart that compares the predicted average price for different year and condition combinations of the same car, 
  - and finally plots the predicted prices across the states on the U.S. map. 

For the best user experience, it is deployed as a webapp on heroku using Flask. One can simply go to https://usedcars-capstone.herokuapp.com/ to give it a try. 

Data: 

1) Kaggle: The data is obtained from kaggle.com. It is apprx 1.4 GB CSV and includes the criagslist ads of apprx 500,000 vehicles. It consists of listing price, manufacturer, model, year, odometer, condition, transmission, region, state, VIN number, ad id, cylinders, fuel, drive, type, lat, long, description. 

2) NewCarTestDrive.com and Google.com: For each car, its MSRP value is scraped from NewCarTestDrive.com if it is available there, otherwise from Google.com. (Including the MSRP values, improved the MAE of the best performing model 68% by decreasing it from 1440 to 453.)

Model: 

Among many estimators, a GroupbyEstimator that uses different Random Forest Regressors for each manufacturer group is adopted. It yields an R2 value of %98.75 (MAE: 453), while it is 92% (MAE: 941) on the test set. 3 different predictors (Linear Refression, Ridge Regression, and Random Forest Regressor) are used in 3 three different settings (A GroupbyEstiamtor for 'state' and 'manufacturer each, and one full model for the entire dataset. The best performing model out of the 9 is adopted to further the analysis. Below is a result that compares different scenerios. (A GridsearchCV predictor is used to optimize the Ridge and the Forest models).  


| Model                 |    Trained      | Train_Error | Test Error |
|-----------------------|-----------------|-------------|------------|
| LinearRegression      | No groupby      |    2210     |    2245    |
| LinearRegression      | On states       |    1982     |    2219    |
| LinearRegression      | On manufacturer |    2142     |    2179    |
| Ridge                 | No groupby      |    2224     |    2252    |
| Ridge                 | On states       |    2012     |    2219    |
| Ridge                 | On manufacturer |    2151     |    2180    |
| RandomForestRegressor | No groupby      |     453     |    1254    |
| RandomForestRegressor | On states       |     617     |    1647    |
| RandomForestRegressor | On manufacturer |     453     |     941    |


The delivirable of this project is a webapp. What it yields and the sources are listed below. 

  - Picture: 
      scraped from www.newcartestdrive.com 
  - Reviews:
      obtained from www.cars.com
  - Complaints:
      mined from www.carcomplaints.com
  - BarChart:
      created using altair
  - Map:
      created using plotly, posted on plotly's chart_sdutio, and referenced in the webapp.  
