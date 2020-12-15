PATH_TO_INTERMEDIATE_DATA = 'preprocessed'
PATH_TO_PREDICTIONS_NO_NOISE = 'linear_regression'

historical_yrs = [i + 14 for i in range(6)]
future_yrs = [5*i + 20 for i in range(7)]

energies = ['peak', 'consumption']
gdp_types = ['log', 'linear', 'exp']

cities = {
    'NR': 
        {
            'Delhi': (28.620198, 77.207953),
            'Jaipur': (26.913310, 75.800162),
            'Lucknow': (26.850000, 80.949997),
            'Kanpur': (26.460681, 80.313318),
            'Ghaziabad': (28.673733, 77.437598),
            'Ludhiana': (30.903434, 75.854784),
            'Agra': (27.188679, 77.985161),
#             'Faridabad':
#             'Varanasi':
#             'Meerut':
#             'Srinagar':
#             'Aurangabad':
#             'Jodhpur':
#             'Chandigarh':
        },
    'WR': 
        {
            'Bombay': (19.136698, 72.874997),
            'Ahmedabad': (23.046722, 72.594153), 
            'Surat': (21.172953, 72.830534),
            'Pune': (18.522325, 73.839962),
            'Nagpur': (21.143781, 79.083838),
            'Thane': (19.208691, 72.986695),
            'Bhopal': (23.229054, 77.454641),
            'Indore': (22.729657, 75.864191),
            'Pimpri-Chinchwad': (18.634826, 73.799352),
#             'Vadodara':
#             'Nashik':
#             'Rajkot':
#             'Vasai-Virar':
#             'Varanasi':
#             'Gwalior':
#             'Jabalpur':
#             'Raipur': (21.250000, 81.629997)
        },
    'ER':
        {
            'Kolkata': (22.602239, 88.384624),
            'Patna': (25.606163, 85.129308),
            # 'Howrah': (22.575807, 88.218517), ignoring b/c close to kolkata
            'Ranchi': (23.369065, 85.323193),
        },
    'SR':
        {
            'Hyderabad': (17.403782, 78.419709),
            'Bangalore': (12.998121, 77.575998),
            'Chennai': (13.057463, 80.237652),
            'Visakhapatnam': (17.722926, 83.235116),
            'Coimbatore': (11.022585, 76.960722),
            'Vijayawada': (16.520201, 80.638189),
            'Madurai': (9.925952, 78.124883),
        },
    'NER':
        {
            'Guwahati': (26.152019, 91.733483),
            'Agartala': (23.841343, 91.283016),
            'Imphal': (24.810497, 93.934348),
        },
}


fields = {
    'QV10M': 'h10m',  # specific humidity 10m above surface
    'QV2M': 'h2m',  # specific humidity 2m above surface
    'T10M': 't10m',  # temperature 10m above surface
    'T2M': 't2m',  # temperature 2m above surface
    'TQI': 'tqi', # total precipitable ice water
    'TQL': 'tql', # total precipitable liquid water
    'TQV': 'tqv', # total precipitable water vapor
    'U10M': 'ew10m', # eastward wind 10m above surface
    'U2M': 'ew2m', # eastward wind 2m above surface
    'V10M': 'nw10m', # northward wind 10m above surface
    'V2M': 'nw2m', # northward wind 2m above surface
}
