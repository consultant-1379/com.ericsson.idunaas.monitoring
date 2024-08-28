import yaml
from kubernetes import client, config
import logsystem

LOG = logsystem.get_logger(__name__)


def read_installed_helm_cm(_namespace, client_api):
    """read installed helm configmap from namespaces"""
    response = client_api.read_namespaced_config_map(name="eric-installed-applications", namespace=_namespace)
    return yaml.safe_load(yaml.safe_load(yaml.dump(response.data))['Installed'])
