#1: Import the required modules
from application.models import PredEntry
import datetime as datetime
import pytest
from flask import json
import os.path

#Unit Test
# Test add prediction entry
@pytest.mark.parametrize("entrylist",
    [
        ["audi", "A1", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 1],
        ["bmw", "1 Series", 2014, "Manual", 2.0, 45000, "Diesel", 20, 60.1, 10000.00, 1],
        ["merc", "A Class", 2019, "Automatic", 1.5, 10000, "Petrol", 150, 55.4, 15000.00, 1],
        ["ford", "Focus", 2018, "Manual", 1.0, 20000, "Petrol", 150, 55.4, 11000.00, 1],
        ["hyundi", "I30", 2016, "Semi-Auto", 1.6, 30000, "Diesel", 20, 60.1, 9000.00, 1],
        ["skoda", "Octavia", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 2],
        ["toyota", "Yaris", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 2],
        ["vauxhall", "Corsa", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 2],
        ["vw", "Golf", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 3]
    ])

def test_add_prediction(client, entrylist, capsys):
    url = '/api/predEntry/add'
    with capsys.disabled():
        data = {
            'brand': entrylist[0],
            'model': entrylist[1],
            'year': entrylist[2],
            'transmission': entrylist[3],
            'engineSize': entrylist[4],
            'mileage': entrylist[5],
            'fuelType': entrylist[6],
            'tax': entrylist[7],
            'mpg': entrylist[8],
            'prediction': entrylist[9],
            'user_id': entrylist[10]
        }
        # Use client object to pass data to the url
        response = client.post(url, data=json.dumps(data), content_type='application/json')
        # Check if the response is 200
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'

# Test get all prediction entries by user id
@pytest.mark.parametrize("entrylist",
    [
        [1],
        [2],
        [3]
    ])

# Test remove prediction entry
def test_get_prediction(client, entrylist, capsys):
    with capsys.disabled():
        # Use client object to pass data to the url
        response = client.get(f"/api/predEntry/{entrylist[0]}")
        # Check if response matches the data
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'
        # Check if something is returned
        assert len(response.json) > 0

# Test remove prediction entry
@pytest.mark.parametrize("entrylist",
    [
        ["audi", "A1", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 1],
        ["bmw", "1 Series", 2014, "Manual", 2.0, 45000, "Diesel", 20, 60.1, 10000.00, 1],
        ["merc", "A Class", 2019, "Automatic", 1.5, 10000, "Petrol", 150, 55.4, 15000.00, 1],
        ["ford", "Focus", 2018, "Manual", 1.0, 20000, "Petrol", 150, 55.4, 11000.00, 1],
        ["hyundi", "I30", 2016, "Semi-Auto", 1.6, 30000, "Diesel", 20, 60.1, 9000.00, 1],
        ["skoda", "Octavia", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 2],
        ["toyota", "Yaris", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 2],
        ["vauxhall", "Corsa", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 2],
        ["vw", "Golf", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4, 12000.00, 3]
    ])

def test_remove_prediction(client, entrylist, capsys):
    with capsys.disabled():
        data = {
            'brand': entrylist[0],
            'model': entrylist[1],
            'year': entrylist[2],
            'transmission': entrylist[3],
            'engineSize': entrylist[4],
            'mileage': entrylist[5],
            'fuelType': entrylist[6],
            'tax': entrylist[7],
            'mpg': entrylist[8],
            'prediction': entrylist[9],
            'user_id': entrylist[10]
        }
        # Add prediction entry
        response = client.post('/api/predEntry/add', data=json.dumps(data), content_type='application/json')
        id = response.json['id']
        assert response.status_code == 200
        assert response.json['id'] > 0
        
        # Remove prediction entry
        response2 = client.get(f'/api/predEntry/remove/{id}')
        assert response2.status_code == 200
        assert response2.headers['Content-Type'] == 'application/json'
        assert int(response2.json['id']) == int(response.json['id'])

# Test export prediction entries
@pytest.mark.parametrize("entrylist",
    [
        [1],
        [2],
        [3]
    ])

def test_export_prediction(client, entrylist, capsys):
    with capsys.disabled():
        # Use client object to pass data to the url
        response = client.get(f"/api/predEntry/export/{entrylist[0]}")
        file_path = os.path.join(os.getcwd(), 'outputs', f'history{entrylist[0]}.csv')

        # Check if response matches the data
        assert response.status_code == 200
        
        # Check if output folder has a file called history{entrylist[0]}.csv
        assert os.path.isfile(file_path) == True

# Consistency Test for Predictions
@pytest.mark.parametrize("predConsistencyList",
    [
        [["audi", "A1", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4],
         ["audi", "A1", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4],
         ["audi", "A1", 2017, "Manual", 1.4, 12500, "Petrol", 150, 55.4], ],
        [["bmw", "1 Series", 2014, "Manual", 2.0, 45000, "Diesel", 20, 60.1],
         ["bmw", "1 Series", 2014, "Manual", 2.0, 45000, "Diesel", 20, 60.1],
         ["bmw", "1 Series", 2014, "Manual", 2.0, 45000, "Diesel", 20, 60.1], ],
        [["merc", "A Class", 2019, "Automatic", 1.5, 10000, "Petrol", 150, 55.4],
         ["merc", "A Class", 2019, "Automatic", 1.5, 10000, "Petrol", 150, 55.4],
         ["merc", "A Class", 2019, "Automatic", 1.5, 10000, "Petrol", 150, 55.4], ],
        [["ford", "Focus", 2018, "Manual", 1.0, 20000, "Petrol", 150, 55.4],
         ["ford", "Focus", 2018, "Manual", 1.0, 20000, "Petrol", 150, 55.4],
         ["ford", "Focus", 2018, "Manual", 1.0, 20000, "Petrol", 150, 55.4], ],       
    ]
)

def test_predictAPI(client, predConsistencyList, capsys):
    with capsys.disabled():
        predictedOutput = []
        for predictions in predConsistencyList:
            data = {
                'brand': predictions[0],
                'model': predictions[1],
                'year': predictions[2],
                'transmission': predictions[3],
                'engineSize': predictions[4],
                'mileage': predictions[5],
                'fuelType': predictions[6],
                'tax': predictions[7],
                'mpg': predictions[8]
            }
            response = client.get('/api/predict', data=json.dumps(data), content_type='application/json')
            response_body = response.json
            assert response.status_code == 200
            assert response_body['prediction']
            predictedOutput.append(response_body['prediction'])
            # Check if the prediction is consistent
            assert len(set(predictedOutput)) == 1
            # Make sure all the predictions are the same
            assert all(x == predictedOutput[0] for x in predictedOutput) == True



        
       


