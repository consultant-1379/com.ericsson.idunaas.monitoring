"""
Check the availability of ENM's user interface
"""

# GENERIC IMPORT ###
import requests


# LOCAL MODULES
import utils
import logsystem

# GLOBAL PARAMETERS ###
LOG = logsystem.get_logger(__name__)


def enm_login_check(url_dict=None, username='', password='', proxies=None):
    LOG.info('Starting UI login checks on ENM UI endpoint')
    url = url_dict['as_string']
    timeout_seconds = 2

    session = requests.Session()
    r = session.post(
            url=url+'/login',
            verify=False, 
            timeout=timeout_seconds, 
            proxies=proxies,
            data=dict(IDToken1=username, IDToken2=password),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects=False
            )
    if r.status_code != 302:
        LOG.info('ENM UI login FAILED (HTTP status code {})'.format(r.status_code))
        return 1
    
    r = session.get(
            url=url,
            verify=False, 
            timeout=timeout_seconds, 
            proxies=proxies)
    if r.status_code == 200:
        LOG.info('ENM UI login OK')
        return 0
    else:
        LOG.info('ENM UI page FAILED (HTTP status code {})'.format(r.status_code))
        return 1

# MAIN FUNCTION ##


def enm_ui_availability(url, user, passwd, proxies=None):
    params = {
        'url':      url,
        'username': user,
        'password': passwd
    }
    # params = utils.get_parames_from_environment_variables('ENMUI_URL', 'ENMUI_USER', 'ENMUI_PASSWD')
    if params['url'] == "" or params['username'] == "" or params['password'] == "":
        return {
            'hostname': '',
            'tcp_check_status':   "1",
            'http_check_status':  "1",
            'login_check_status': "1",
            'overall_status':     1.0
        }  
        
    return utils.check_endpoint(login_fcn=enm_login_check, **params, proxies=proxies)
