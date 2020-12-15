# Demand Forecasting Model
Bottom-up energy demand forecasting for India in 2050

* Business-As-Usual Model
The BAU folder includes all the data as well as code to run the regression mode
Running predict.py will produce three sets of predictions at regional levels. add_noise.py will additionally produce natural noise variation. Results are GDP projections dependent, if projections are changed users must maintain consistency of projections with the Technology model.

* Technology Model
forecast.py is a set of functions that build hourly demand of various technologies. results.py will generate all the hourly profiles at different resolutions.

