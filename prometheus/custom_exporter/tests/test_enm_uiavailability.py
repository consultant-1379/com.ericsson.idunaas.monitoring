from unittest import mock
import requests_mock

import enm_uiavailability


def test_enm_login_check_success():
    """
    Tests login check Success case
    """
    url_dict = {'as_string': 'https://enm.example.com'}
    username = 'testuser'
    password = 'testpass'

    result = -100
    with requests_mock.Mocker() as mocker:
        mocker.post(
            url=url_dict['as_string'] +
            '/login',
            status_code=302,
            json={})
        mocker.get(url=url_dict['as_string'], status_code=200)
        result = enm_uiavailability.enm_login_check(
            url_dict, username, password)

    assert result == 0


def test_enm_login_check_failure_login():
    """
    Tests login check Failure case
    """
    url_dict = {'as_string': 'https://enm.example.com'}
    username = 'testuser'
    password = 'testpass'
    result = -100
    with requests_mock.Mocker() as mock:
        mock.post(
            url=url_dict['as_string'] +
            '/login',
            status_code=403,
            json={})
        result = enm_uiavailability.enm_login_check(
            url_dict, username, password)
        assert result == 1


def test_enm_login_check_failure_ui():
    """
    Tests UI check Failure case
    """
    url_dict = {'as_string': 'https://enm.example.com'}
    username = 'testuser'
    password = 'testpass'
    result = -100
    with requests_mock.Mocker() as mock:
        mock.post(
            url=url_dict['as_string'] +
            '/login',
            status_code=302,
            json={})
        mock.get(url=url_dict['as_string'], status_code=403)
        result = enm_uiavailability.enm_login_check(
            url_dict, username, password)
        assert result == 1


def test_enm_ui_availability():
    """
    Tests ENM UI availability function
    """
    with mock.patch('utils.check_endpoint') as mock_check_endpoint:
        mock_check_endpoint.return_value = {'overall_status': 0.0}
        result = enm_uiavailability.enm_ui_availability(
            'http://example.com', 'user', 'passwd')
        assert result == {'overall_status': 0.0}
        result = enm_uiavailability.enm_ui_availability('', '', '')
        assert result == {
            'hostname': '',
            'tcp_check_status': "1",
            'http_check_status': "1",
            'login_check_status': "1",
            'overall_status': 1.0
        }
