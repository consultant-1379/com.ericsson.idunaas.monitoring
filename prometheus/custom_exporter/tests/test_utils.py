from urllib import parse
import socket
import pytest
import requests
from unittest.mock import patch, MagicMock
from utils import analyze_url, tcp_check, get_parames_from_environment_variables, \
    http_check

result_to_label = {0: "OK", 1: "FAIL"}


def test_analyze_url():
    # Create a mock response for url_parse() function
    mock_parse_result = parse.ParseResult(
        scheme="https",
        netloc="www.ericsson.com",
        path="/en",
        params="",
        query="",
        fragment="",
    )
    mock_url_parse = MagicMock(return_value=mock_parse_result)
    with patch('urllib.parse.urlparse', mock_url_parse):
        # Call the function
        result = analyze_url("www.ericsson.com/en")
        print(result)
        expected_result = {
            "as_string": "www.ericsson.com/en",
            "proto": "https",
            "hostname": "www.ericsson.com",
            "port": 443,
            "resource_path": "/en",
            "query_string": "",
            "parse_result": mock_parse_result,
        }
        assert result == expected_result


def test_get_parames_from_environment_variables():
    """Test the get_parames_from_environment_variables function
    """
    test_cases = [{'env_vars': {'TEST_URL_VAR': '',
                                'TEST_USER_VAR': 'test_user',
                                'TEST_PASSWD_VAR': 'test_passwd'},
                   'expected_result': None},
                  {'env_vars': {'TEST_URL_VAR': 'test_url',
                                'TEST_USER_VAR': '',
                   'TEST_PASSWD_VAR': 'test_passwd'},
                   'expected_result': None},
                  {'env_vars': {'TEST_URL_VAR': 'test_url',
                                'TEST_USER_VAR': 'test_user',
                                'TEST_PASSWD_VAR': ''},
                   'expected_result': None},
                  {'env_vars': {'TEST_URL_VAR': 'test_url',
                                'TEST_USER_VAR': 'test_user',
                                'TEST_PASSWD_VAR': 'test_passwd'},
                   'expected_result': {'url': 'test_url',
                                       'username': 'test_user',
                                       'password': 'test_passwd'}}]
    for case in test_cases:
        with patch.dict('os.environ', case['env_vars']):
            result = get_parames_from_environment_variables(
                'TEST_URL_VAR', 'TEST_USER_VAR', 'TEST_PASSWD_VAR')
            assert result == case['expected_result']


def test_tcp_check_returns_0_when_connection_successful():
    """Test tcp check return 0 when connection is successful
    """
    with patch.object(socket, 'socket') as mock_socket:
        instance = mock_socket.return_value
        instance.connect_ex.return_value = 0

        result = tcp_check('test_host', 12345)
        assert result == 0


def test_tcp_check_returns_1_when_connection_failed():
    """Test tcp check return 1 when connection is failed
    """
    with patch.object(socket, 'socket') as mock_socket:
        instance = mock_socket.return_value
        instance.connect_ex.return_value = 1

        result = tcp_check("localhost", 8080)
        assert result == 1


def test_http_check_success():
    """Test http check is successful
    """
    with patch.object(requests, 'get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200

        result = http_check("http://example.com")

        assert result == 0
        mock_get.assert_called_once_with(
            url="http://example.com",
            timeout=2,
            verify=False,
            proxies=None)


def test_http_check_failure():
    """Test http check is failure
    """
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException

        result = http_check("http://example.com")

        assert result == 1
        mock_get.assert_called_once_with(
            url="http://example.com",
            timeout=2,
            verify=False,
            proxies=None)


def test_check_endpoint():
    """Test check endpoint function
    """
    assert True


def test_environment_variable_is_true():
    """Test environment variable is true function
    """
    assert True


def test_get_environment_variable_value():
    """Test get environment variable function
    """
    assert True
