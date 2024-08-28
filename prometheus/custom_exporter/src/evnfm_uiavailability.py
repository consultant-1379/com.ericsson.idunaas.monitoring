"""
Check the availability of EVNFM's user interface
"""
# GENERIC IMPORT ###
import requests
import json


### LOCAL MODULES ###
import utils
import logsystem


# GLOBAL PARAMETERS ###
LOG = logsystem.get_logger(__name__)


def execute_rest_api(url, http_method="HttpMethod.GET", data=None, headers=None, token=None, proxies=None, timeout_seconds=2):
    """Generic handler http/https call."""
    if token is not None and token != '':
        final_headers = {'Content-Type': 'application/json',
                         # 'Accept': 'application/json',
                         'Cookie': 'JSESSIONID=' + token}
    else:
        final_headers = headers
    try:
        if http_method == "HttpMethod.GET":
            response = requests.get(url=url, headers=final_headers, data=data, verify=False, proxies=proxies, timeout=timeout_seconds)
        elif http_method == "HttpMethod.POST":
            response = requests.post(url=url, headers=final_headers, data=data, verify=False, proxies=proxies, timeout=timeout_seconds)

    except requests.exceptions.RequestException as err:
        result = "Unable to execute rest call " + str(url)
        status_code = 502
        LOG.error(f'{result}. HTTP code set to {status_code}', exc_info=True)
        return status_code, result
    try:
        result = json.loads(response.text)
    except ValueError:
        LOG.error('Impossible to parse json', exc_info=True)
        result = response.text
    LOG.debug(f"execute_rest_api: status_code={response.status_code}, response={result}", exc_info=True)
    return response.status_code, result


def set_rest_api_token(username, password, url, proxies=None):
    """Authorisation on EVNFM server and getting JWT."""
    headers = {'content-type': 'application/json',
               'X-Login': username,
               'X-Password': password}
    url = url + '/auth/v1'
    status_code, response = execute_rest_api(url=url, http_method="HttpMethod.POST", headers=headers, proxies=proxies)
    return status_code, response


# Check UI accessibilty
def evnfm_login_check(url_dict=None, username='', password='', proxies=None):
    LOG.info('Starting UI login checks on EVNFM UI endpoint')

    url = url_dict['hostname']
    if not url.lower().startswith(('http://', 'https://')):
        url = "https://" + url

    status, token = set_rest_api_token(username=username, password=password, url=url, proxies=proxies)
    LOG.debug('status={} token={}'.format(status, token))
    if status == 200:
        url = url + '/vnfm'
        login_status, login = execute_rest_api(url=url, http_method="HttpMethod.GET", data=None, headers=None, token=token, proxies=proxies)
        if login_status == 200:
            LOG.info('UI login to EVNFM succeeded')
            return 0

    LOG.info('UI login to EVNFM failed')
    return 1


def evnfm_ui_availability(url, user, passwd, proxies=None):
    params = {
        'url':      url,
        'username': user,
        'password': passwd
    }
    # params = utils.get_parames_from_environment_variables('EVNFMUI_URL', 'EVNFMUI_USER', 'EVNFMUI_PASSWD')
    if params['url'] == "" or params['username'] == "" or params['password'] == "":
        return {
            'hostname': '',
            'tcp_check_status':   "1",
            'http_check_status':  "1",
            'login_check_status': "1",
            'overall_status':     1.0
        }  

    return utils.check_endpoint(login_fcn=evnfm_login_check, **params, proxies=proxies)
