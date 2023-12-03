#1: Import the required modules
import datetime as datetime
import pytest
from flask import json

# Test all the front end routes
@pytest.mark.parametrize("entrylist",
        [
         ["/"],
         ["/about"],
         ["/predict"],
         ["/history"],
         ["/register"],
         ["/login"],
         ["/profile"]
        ])
def test_front_end_routes(client, entrylist, capsys):
    with capsys.disabled():
        # Login user
        data = {
            'email': "testingAccount2@gmail.com",
            'password': "abc123abc123",
            'remember': False
        }

        response = client.post('/api/user', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200

        # Test the front end routes
        response2 = client.get(entrylist[0])
        assert response2.status_code == 200
        assert response2.headers['Content-Type'] == 'text/html; charset=utf-8'
