import requests

from unittest import mock
import requests_mock

import evnfm_uiavailability


def test_execute_rest_api_with_mocked_exception():
    """
    Tests the execute_rest_api method with mocked exception
    """
    # create a mock object for the requests library's get method
    with mock.patch('requests.get', side_effect=requests.exceptions.RequestException):
        # call the execute_rest_api function with the mocked requests library
        status_code, result = evnfm_uiavailability.execute_rest_api(
            url='https://www.example.com')

        # assert that the expected status code and result are returned
        assert status_code == 502
        assert result == "Unable to execute rest call https://www.example.com"


def test_execute_rest_api_with_mocked_json_decode_error():
    """
    Tests the execute_rest_api method with json decode error
    """
    # create a mock object for the requests library's get method
    response_mock = mock.MagicMock(status_code=200, text='invalid json')
    with mock.patch('requests.get', return_value=response_mock):
        # call the execute_rest_api function with the mocked requests library
        status_code, result = evnfm_uiavailability.execute_rest_api(
            url='https://www.example.com')

        # assert that the expected status code and result are returned
        assert status_code == 200
        assert result == "invalid json"


def test_execute_rest_api_with_valid_inputs():
    """
    Tests the execute_rest_api method with invalid inputs
    """
    # create a mock object for the requests library's get method
    with mock.patch('requests.get', return_value=mock.MagicMock(text='{"key": "value"}', status_code=200)):
        # call the execute_rest_api function with the mocked requests library
        status_code, result = evnfm_uiavailability.execute_rest_api(
            url='https://www.example.com')

        # assert that the expected status code and result are returned
        assert status_code == 200
        assert result == {"key": "value"}


def test_set_rest_api_token_success():
    """
    Tests the set_rest_api_token method success case
    """
    with requests_mock.Mocker() as mock:
        mock.post(
            '/auth/v1',
            status_code=200,
            json={
                'jwt_token': 'abcdefghijklmnopqrstuvwxyz'})
        status_code, response = evnfm_uiavailability.set_rest_api_token(
            username='test_user', password='test_pass', url='http://so.463637415265.eu-west-1.ac.ericsson.se')
        assert status_code == 200
        assert response == {'jwt_token': 'abcdefghijklmnopqrstuvwxyz'}


def test_set_rest_api_token_failed():
    """
    Tests the set_rest_api_token method failure case
    """
    with requests_mock.Mocker() as mock:
        mock.post('/auth/v1', status_code=401)
        status_code, response = evnfm_uiavailability.set_rest_api_token(
            username='test_user', password='test_pass', url='http://so.463637415265.eu-west-1.ac.ericsson.se')
        assert status_code == 401


def test_evnfm_login_check_success():
    """
    Tests the evnfm login check method success case
    """
    # Arrange
    url_dict = {'hostname': 'https://so.463637415265.eu-west-1.ac.ericsson.se'}
    username = 'so-user'
    password = 'soPassword'
    proxies = None
    token = 'abc123'

    result = -100
    # Setting up mock objects
    with mock.patch('evnfm_uiavailability.set_rest_api_token') as mock_set_rest_api_token:
        mock_set_rest_api_token.return_value = (200, token)

        with mock.patch('evnfm_uiavailability.execute_rest_api') as mock_execute_rest_api:
            mock_execute_rest_api.return_value = (200, {})

            # Act
            result = evnfm_uiavailability.evnfm_login_check(
                url_dict, username, password, proxies)

    # Assert
    assert result == 0


def test_evnfm_login_check_fail():
    """
    Tests the evnfm login check method failure case
    """
    # Arrange
    url_dict = {'hostname': 'https://so.463637415265.eu-west-1.ac.ericsson.se'}
    username = 'so-user'
    password = 'soPassword'
    proxies = None
    token = 'abc123'

    result = -100
    # Setting up mock objects
    with mock.patch('evnfm_uiavailability.set_rest_api_token') as mock_set_rest_api_token:
        mock_set_rest_api_token.return_value = (200, token)

        with mock.patch('evnfm_uiavailability.execute_rest_api') as mock_execute_rest_api:
            mock_execute_rest_api.return_value = (401, {})

            # Act
            result = evnfm_uiavailability.evnfm_login_check(
                url_dict, username, password, proxies)

    # Assert
    assert result == 1


def test_evnfm_ui_availability():
    """
    Tests the evnfm ui availability  method
    """
    with mock.patch('utils.check_endpoint') as mock_check_endpoint:
        mock_check_endpoint.return_value = {
            'hostname': 'so.463637415265.eu-west-1.ac.ericsson.se',
            'tcp_check_status': "0",
            'http_check_status': "0",
            'login_check_status': "0",
            'overall_status': 0.0
        }
        result = evnfm_uiavailability.evnfm_ui_availability(
            'https://so.463637415265.eu-west-1.ac.ericsson.se', 'so-user', 'soPassword')
        assert result == {
            'hostname': 'so.463637415265.eu-west-1.ac.ericsson.se',
            'tcp_check_status': "0",
            'http_check_status': "0",
            'login_check_status': "0",
            'overall_status': 0.0
        }
        result = evnfm_uiavailability.evnfm_ui_availability('', '', '')
        assert result == {
            'hostname': '',
            'tcp_check_status': "1",
            'http_check_status': "1",
            'login_check_status': "1",
            'overall_status': 1.0
        }
