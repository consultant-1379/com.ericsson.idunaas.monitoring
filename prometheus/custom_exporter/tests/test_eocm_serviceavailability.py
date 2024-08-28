from unittest import mock
import pytest
from eocm_serviceavailability import eocm_service_availability


def test_eocm_service_availability_success():
    """ 
    Test EOCM service availability success case
    """
    url = 'example.com'
    user = 'user'
    passwd = 'passwd'
    cmd = 'ls'

    # stub the SSHClient.connect method to return None
    with mock.patch("paramiko.SSHClient.connect") as ssh_connect:
        ssh_connect.return_value = None

        # stub the SSHClient.exec_command method to return fake output
        with mock.patch("paramiko.SSHClient.exec_command") as ssh_exec_command:
            stdout = mock.Mock()
            stdout.readlines.return_value = ['Fails    = 0', 'Errors   = 0']
            ssh_exec_command.return_value = (None, stdout, None)

            result = eocm_service_availability(url, user, passwd, cmd)
            assert result == {
                'hostname': url,
                'overall_status': 0
            }


def test_eocm_service_availability_failure():
    """ 
    Test EOCM service availability failure case
    """
    url = 'example.com'
    user = 'user'
    passwd = 'passwd'
    cmd = 'ls'

    # stub the SSHClient.connect method to raise an exception
    with mock.patch("paramiko.SSHClient.connect") as ssh_connect:
        ssh_connect.side_effect = Exception("Impossible to perform SSH check.")
        with pytest.raises(Exception) as e:
            eocm_service_availability(url, user, passwd, cmd)
        assert str(e.value) == "Impossible to perform SSH check."
