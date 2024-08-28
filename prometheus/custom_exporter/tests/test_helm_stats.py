import yaml
from unittest.mock import MagicMock, patch
import pytest
from kubernetes import client
from helm_stats import read_installed_helm_cm


def test_read_installed_helm_cm_success():
    """Test read installed helm cm success case
    """
    # Create a mock response
    mock_response = MagicMock()
    mock_response.data = {
        'Installed': yaml.dump({
            "csar": [{"name": "csar1", "version": "1.0.0"}],
            "helmfile": {"name": "helmfile1", "release": "2.0.0"},
            "deployment-manager": "3.0.0",
            "tags": {"app1": "active", "app2": "inactive"}
        })
    }

    # Use a mock for the `read_namespaced_config_map` method
    with patch.object(client.CoreV1Api, 'read_namespaced_config_map', return_value=mock_response):
        # Call the function
        result = read_installed_helm_cm("test-namespace", client.CoreV1Api)
        expected_result = {
            "csar": [{"name": "csar1", "version": "1.0.0"}],
            "helmfile": {"name": "helmfile1", "release": "2.0.0"},
            "deployment-manager": "3.0.0",
            "tags": {"app1": "active", "app2": "inactive"}
        }
        assert result == expected_result


def test_read_installed_helm_cm_failure():
    """Test read installed helm cm failure case
    """
    # Use a mock for the `read_namespaced_config_map` method that raises an
    # exception
    with patch.object(client.CoreV1Api, 'read_namespaced_config_map', side_effect=Exception("Test exception")):
        # Call the function
        with pytest.raises(Exception, match="Test exception"):
            read_installed_helm_cm("test-namespace", client.CoreV1Api)
