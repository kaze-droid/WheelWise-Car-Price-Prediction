#1: Import the required modules
from application.models import User
import datetime as datetime
import pytest
from flask import json
import os.path

#Unit Test
# Add user (sign up) with validation failure testing
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        pytest.param(["testuser5", "testingAccount1@gmail.com", "abc123abc123"], marks=pytest.mark.xfail(reason="Email already exists", strict=True)),
        pytest.param(["testuser6", "testingAccount2@gmail.com", "abc123abc123"], marks=pytest.mark.xfail(reason="Email already exists", strict=True)),
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])

def test_add_user(client, entrylist, capsys):
    url = '/api/user/add'
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'creation_date': datetime.datetime.now(),
        }
        # Use client object to pass data to the url
        response = client.post(url, data=json.dumps(data), content_type='application/json')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'
        assert response.json['id'] > 0

# Login user with validation failure testing
@pytest.mark.parametrize("entrylist",
    [
        ["testuser", "testingAccount1@gmail.com", "abc123abc123"],
        pytest.param(["testuser2", "testingAccount2@yahoo.com", "abc123abc123"], marks=pytest.mark.xfail(reason="Email does not exist", strict=True)),
        pytest.param(["testuser3", "testingAccount3@gmail.com", "abc123"], marks=pytest.mark.xfail(reason="Invalid Credentials", strict=True)),
    ])

def test_login_user(client, entrylist, capsys):
    url = '/api/user'
    with capsys.disabled():
        data = {
            'email': entrylist[1],
            'password': entrylist[2],
            'remember': False
        }
        # Use client object to pass data to the url
        response = client.post(url, data=json.dumps(data), content_type='application/json')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'
        assert response.json['id'] > 0


# Change username
@pytest.mark.parametrize("entrylist",
    [
        ["testuser", "testingAccount1@gmail.com", "abc123abc123"],
        ["testuser2", "testingAccount2@gmail.com", "abc123abc123"],
        ["testuser3", "testingAccount3@gmail.com", "abc123abc123"]
    ])

def test_change_username(client, entrylist, capsys):
    url = '/api/user/changeUsername'
    with capsys.disabled():
        # Login as current user
        data =  {
            'email': entrylist[1],
            'password': entrylist[2],
            'remember': False
        }

        response1 = client.post('/api/user', data=json.dumps(data), content_type='application/json')
        assert response1.status_code == 200

        # Change username
        data = {
            'username': entrylist[0]
        }

        # Use client object to pass data to the url
        response2 = client.post(url, data=json.dumps(data), content_type='application/json')
        # Check if the response is 200
        assert response2.status_code == 200
        assert response2.headers['Content-Type'] == 'application/json'
        assert response1.json['id'] == response2.json['id']

# Change password
@pytest.mark.parametrize("entrylist",
    [
        ["testuser", "testingAccount1@gmail.com", "abc123abc123", "123abc123abc"],
        ["testuser2", "testingAccount2@gmail.com", "abc123abc123", "123abc123abc"],
        ["testuser3", "testingAccount3@gmail.com", "abc123abc123", "123abc123abc"]
    ])

def test_change_password(client, entrylist, capsys):
    url = '/api/user/changePassword'
    with capsys.disabled():
        # Login as current user
        data =  {
            'email': entrylist[1],
            'password': entrylist[2],
            'remember': False
        }

        response1 = client.post('/api/user', data=json.dumps(data), content_type='application/json')
        assert response1.status_code == 200

        # Change password
        data = {
            'password': entrylist[3]
        }

        # Use client object to pass data to the url
        response2 = client.post(url, data=json.dumps(data), content_type='application/json')
        # Check if the response is 200
        assert response2.status_code == 200
        assert response2.headers['Content-Type'] == 'application/json'
        assert response1.json['id'] == response2.json['id']

        # Revert password (so tests are idempotent)
        data = {
            'password': entrylist[2]
        }

        # Use client object to pass data to the url
        response3 = client.post(url, data=json.dumps(data), content_type='application/json')
        # Check if the response is 200
        assert response3.status_code == 200
        assert response3.headers['Content-Type'] == 'application/json'
        assert response1.json['id'] == response3.json['id']

# Remove user
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"]
    ])

def test_remove_user(client, entrylist, capsys):
    url = '/api/user/deleteAccount'
    with capsys.disabled():
        # Login as current user
        data =  {
            'email': entrylist[1],
            'password': entrylist[2],
            'remember': False
        }

        response1 = client.post('/api/user', data=json.dumps(data), content_type='application/json')
        assert response1.status_code == 200

        data = {
            'username': entrylist[0],
            'password': entrylist[2],
        }

        # Remove user
        response2 = client.post(url, data=json.dumps(data), content_type='application/json')
        assert response2.status_code == 200
        assert response2.headers['Content-Type'] == 'application/json'
        assert response1.json['id'] == response2.json['id']

# Test logout user (logout) with expected failure testing
@pytest.mark.xfail(reason="User is not logged in", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        ["testuser", "testingAccount1@gmail.com", "abc123abc123"],
        ["testuser2", "testingAccount2@gmail.com", "abc123abc123"],
        ["testuser3", "testingAccount3@gmail.com", "abc123abc123"]
    ])

def test_logout_user(client, entrylist, capsys): 
        # Login as current user
        data =  {
            'email': entrylist[1],
            'password': entrylist[2],
            'remember': False
        }

        response1 = client.post('/api/user', data=json.dumps(data), content_type='application/json')
        assert response1.status_code == 200
        assert response1.json['id'] > 0

        # Logout user
        response2 = client.post('/api/user/logout')

        # Check if the response is 200
        assert response2.status_code == 200
        assert response2.headers['Content-Type'] == 'application/json'
        assert response2.json['result'] == 'ok'

        # Test if logout user can change username
        data = {
            'username': entrylist[0]
        }

        # Use client object to pass data to the url
        response3 = client.post('/api/user/changeUsername', data=json.dumps(data), content_type='application/json')
        # Check if the response is 200 (should be 401)
        assert response3.status_code == 200
        


