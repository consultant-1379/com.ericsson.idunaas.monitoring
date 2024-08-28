"""
Common functions that any checkers can use
"""

import socket
import requests
import os

from urllib import parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import logsystem

LOG = logsystem.get_logger(__name__)
result_to_label={ 0: "OK", 1: "FAIL"}
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) # accept all HTTPS certificates


def analyze_url(url):
    """Produce a dictionary. For example if 'https://www.ericsson.com/en' is given,
       this function create the following python dictionary:
        as_string:      'https://www.ericsson.com/en'
        proto:          'https'
        hostname:       'www.ericsson.com'
        port:           443
        resource_path:  '/en'
        query_string:   ''
        parse_result:   exactly what urllib.parse.urlparse return (after adding the protocol in case is missing)
    """
    url_dict = dict(as_string=url)

    if len(url.split('://')) == 1:
        url = 'https://'+url

    url_parsed = parse.urlparse(url)
    url_dict['proto'] = url_parsed.scheme

    url_dict['hostname'] = url_parsed.hostname

    if url_parsed.port is None:
        if url_dict['proto'] == 'http':
            url_dict['port'] = 80
        else:
            url_dict['port'] = 443
    else:
        url_dict['port'] = url_parsed.port

    url_dict['resource_path'] = url_parsed.path
    url_dict['query_string']  = url_parsed.query
    url_dict['parse_result']  = url_parsed
    return url_dict


def get_parames_from_environment_variables(url_var_name, user_var_name, passwd_var_name):

    for name in [url_var_name, user_var_name, passwd_var_name]:
        try:
            s = os.environ[name]
            if s is None or s == '':
                LOG.info('Environment variable {} not found'.format(name))
                return None
        except Exception as e:
            LOG.error('Environment variable {} not found'.format(name), exc_info=True)
            return None

    params = {
        'url':      os.environ[url_var_name],
        'username': os.environ[user_var_name],
        'password': os.environ[passwd_var_name]
    }
    return params


def tcp_check(host, port, timeout_seconds=2):
    """Test the TCP connection"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_seconds)
    try:
        result = sock.connect_ex((host,port))
        if result != 0:
            result=1
    except Exception as e:
        LOG.error('TCP connection failed', exc_info=True)
        result = 1
    sock.close()
    LOG.debug('result='+str(result))
    LOG.info("TCP_CHECK Host: {}, Port: {} - {}".format(host, port, result_to_label[result]) )
    return result


def http_check(url, timeout_seconds=2, proxies=None):
    """Test HTTP protocol"""
    last_url=''
    http_code=''
    try:
        r = requests.get(url=url,
                         verify=False,
                         timeout=timeout_seconds,
                         proxies=proxies)
        try:
            last_url = r.url
            http_code = r.status_code
        except Exception as e:
            LOG.error('Missing filed from response object', exc_info=True)

        if r.status_code == 200:
            result = 0
        else:
            result = 1
    except Exception as e:
        LOG.error('HTTP call failed.', exc_info=True)
        result = 1
    LOG.debug('result='+str(result))
    LOG.info("HTTP_CHECK first_url: {}, last_url: {} http_code: {} - {}".format(url, last_url, http_code, result_to_label[result]))
    return result


def dummy_login_check(url_dict=None,username='', password='',proxies=None):
    """This login check does nothing: use only if login is not required"""
    return 0


def check_endpoint(url, username='', password='', login_fcn=dummy_login_check, proxies=None):
    """Checks the TCP connection, HTTP protocol, and (optionally) try to login"""
    if url is None or url == '':
        return {'hostname': '', 'overall_status': '1'}
    url_dict = analyze_url(url)
    LOG.debug(url_dict)

    tcp_check_status = tcp_check(url_dict['hostname'], url_dict['port'])
    http_check_status = http_check(url=url, proxies=proxies) if tcp_check_status == 0 else 1
    try:
        login_check_status = login_fcn(url_dict, username, password, proxies) if http_check_status == 0 else 1
    except Exception as e:
        LOG.error('Login failed.', exc_info=True)
        login_check_status = 1

    health_status = {
        'hostname': url_dict['hostname'],
        'tcp_check_status': str(tcp_check_status),
        'http_check_status': str(http_check_status),
        'login_check_status': str(login_check_status)
    }

    health_status['overall_status'] = tcp_check_status or \
                                      http_check_status or \
                                      login_check_status

    LOG.debug(health_status)
    return health_status


def environment_variable_is_true(var_name):
    return bool(var_name in os.environ and os.environ[var_name].lower() == 'true')


def get_environment_variable_value(var_name):
    return os.environ[var_name] if var_name in os.environ else None


def get_kpi_metric_keys(resource_type):
    if resource_type == "deployments":
        return ['deployment_name', 'deployment_replicas', 'deployment_replicas_available']
    elif resource_type == "sts":
        return ['sts_name', 'sts_replicas', 'sts_replicas_available']
    elif resource_type == "pods":
        return ['pod_name', 'deployment_sts_name', 'pod_current_state', 'pod_restart_count', 'pod_container_count',
                'pod_container_up_count']
    else:
        LOG.error(f'Invalid Resource type polled for metric key fetch operation')
        return []

