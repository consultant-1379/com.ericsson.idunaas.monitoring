"""
Check the availability of EO-CM's user interface
"""

# GENERIC IMPORT ###
import requests
import json


# LOCAL MODULES
import utils
import logsystem


# GLOBAL PARAMETERS ###
LOG = logsystem.get_logger(__name__)


def eocm_login_check(url_dict=None, username='', password='', proxies=None):
    LOG.info('Starting UI login checks on EO-CM UI endpoint')
    timeout_seconds = 2
    
    auth_url = url_dict['proto']+'://'+url_dict['hostname'] + '/openam/json/realms/root/realms/ecm/authenticate'
    restricted_url = url_dict['proto']+'://'+url_dict['hostname'] + '/openam/json/realms/root/realms/ecm/users/ecmadmin'

    session = requests.Session()
    r = session.post(
        url=auth_url,
        verify=False, 
        timeout=timeout_seconds, 
        proxies=proxies,
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Content-Length': '0',
            'Accept-API-Version': 'protocol=1.0,resource=2.1',  # This is very important!
            'X-Password': 'anonymous',
            'X-Username': 'anonymous',
            'X-NoSession': 'true'
        },
        allow_redirects=False
        )
    if r.status_code != 200:
        LOG.info('EOCM UI login FAILED (HTTP status code {})'.format(r.status_code))
        return 1

    try:
        json_form = json.loads(r.text)
        json_form['callbacks'][0]['input'][0]['value'] = username
        json_form['callbacks'][1]['input'][0]['value'] = password

    except json.decoder.JSONDecodeError:
        LOG.error('EOCM UI login FAILED: cannot decode json response', exc_info=True)
        LOG.debug('HTTP status code: {}    HTTP response body: {}'
                  .format(r.status_code, r.text))
        return 1
    except KeyError:
        LOG.error('EOCM UI login FAILED: missing key in json response', exc_info=True)
        LOG.debug('HTTP status code: {}    HTTP response body: {}'
                  .format(r.status_code, r.text))
        return 1

    r = session.post(
        json=json_form,
        url=auth_url,
        verify=False, 
        timeout=timeout_seconds, 
        proxies=proxies,
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Content-Length': '0',
            'Accept-API-Version': 'protocol=1.0,resource=2.1',  # This is very important!
            'X-Password': 'anonymous',
            'X-Username': 'anonymous',
            'X-NoSession': 'true'
        },
        allow_redirects=False
        )

    if r.status_code != 200:
        LOG.info('EOCM UI login FAILED (HTTP status code {})'.format(r.status_code))
        LOG.debug('HTTP Response body: {}'.format(r.text))
        return 1
    
    r = session.get(
            url=restricted_url,
            verify=False, 
            timeout=timeout_seconds, 
            proxies=proxies)
    if r.status_code == 200:
        LOG.info('EOCM UI login OK')
        return 0
    elif r.status_code == 401:
        LOG.info('EOCM UI login FAILED: HTTP 401 Unauthorized (probably bad credentials)')
        LOG.debug('HTTP Response body: {}'.format(r.text))
        return 1
    else:
        LOG.info('EOCM UI page FAILED (HTTP status code {})'.format(r.status_code))
        LOG.debug('HTTP Response body: {}'.format(r.text))
        return 1


def eocm_ui_availability(url, user, passwd, proxies=None):
    params = {
        'url':      url,
        'username': user,
        'password': passwd
    }
    # params = utils.get_parames_from_environment_variables('EOCMUI_URL', 'EOCMUI_USER', 'EOCMUI_PASSWD')
    if params['url'] == "" or params['username'] == "" or params['password'] == "":
        return {
            'hostname': '',
            'tcp_check_status':   "1",
            'http_check_status':  "1",
            'login_check_status': "1",
            'overall_status':     1.0
        }  

    return utils.check_endpoint(login_fcn=eocm_login_check, **params, proxies=proxies)
