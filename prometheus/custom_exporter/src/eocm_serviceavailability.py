import paramiko
from paramiko.ssh_exception import BadHostKeyException, SSHException, AuthenticationException
import logsystem

LOG = logsystem.get_logger(__name__)


def eocm_service_availability(url, user, passwd, cmd):
    fails = 1
    errors = 1
    port = 22
    # host = os.environ.get('EOCM_SA_HOST')
    # username = os.environ.get('EOCM_SA_USER')
    # password = os.environ.get('EOCM_SA_PASSWORD')
    # command = os.environ.get('EOCM_SA_COMMAND')
    host = url
    username = user
    password = passwd
    command = cmd
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(command)

        lines = stdout.readlines()
        for line in lines:
            if "Fails    = 0" in line:
                fails = 0
            if "Errors   = 0" in line:
                errors = 0
    except (BadHostKeyException, AuthenticationException,
            SSHException, TimeoutError):
        LOG.error('Impossible to perform SSH check.', exc_info=True)

    if fails != 0 or errors != 0:
        status = 1
    else:
        status = 0

    return {
        'hostname': host,
        'overall_status': status
    }
