import pytest
from unittest import mock
import requests_mock

import eocm_uiavailability


@pytest.mark.parametrize(
    "url_dict, username, password, expected_status_code",
    [
        ({'proto': 'http', 'hostname': '127.0.0.1'}, 'testuser', 'testpass', 0),
        ({'proto': 'https', 'hostname': 'localhost'}, 'testuser', 'testpass', 0),
        ({'proto': 'http', 'hostname': '127.0.0.1'}, '', 'testpass', 0),
        ({'proto': 'http', 'hostname': '127.0.0.1'}, 'testuser', '', 0),
        ({'proto': 'http', 'hostname': '127.0.0.1'}, '', '', 0),
    ]
)
def test_eocm_login_check(url_dict, username, password, expected_status_code):
    """Tests EOCM login check

    Args:
        url_dict (dictionary): dictionary of protocol and hostname
        username (text): username
        password (text): password
        expected_status_code (integer): status code 0 or 1
    """
    auth_url = 'http://baseurl.com/auth'
    restricted_url = 'http://baseurl.com/restriced'
    if url_dict:
        auth_url = url_dict['proto'] + '://' + url_dict['hostname'] + \
            '/openam/json/realms/root/realms/ecm/authenticate'
        restricted_url = url_dict['proto'] + '://' + url_dict['hostname'] + \
            '/openam/json/realms/root/realms/ecm/users/ecmadmin'
    result = -100

    with requests_mock.Mocker() as mocker:
        mocker.post(url=auth_url, status_code=200, json={
            'callbacks': [
                {'input': [{'value': 'username'}]},
                {'input': [{'value': 'password'}]}
            ]
        })
        mocker.get(url=restricted_url, status_code=200)
        result = eocm_uiavailability.eocm_login_check(
            url_dict, username, password)

    assert result == expected_status_code


def test_eocm_ui_availability():
    """
    Test EOCM UI availability function
    """
    with mock.patch('utils.check_endpoint') as mock_check_endpoint:
        mock_check_endpoint.return_value = {'overall_status': 0.0}
        result = eocm_uiavailability.eocm_ui_availability(
            'http://example.com', 'user', 'passwd')
        assert result == {'overall_status': 0.0}

        result = eocm_uiavailability.eocm_ui_availability('', '', '')
        assert result == {
            'hostname': '',
            'tcp_check_status': "1",
            'http_check_status': "1",
            'login_check_status': "1",
            'overall_status': 1.0
        }
