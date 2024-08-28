import os
import subprocess
import logsystem
from kubernetes import client, config
from utils import get_environment_variable_value

LOG = logsystem.get_logger(__name__)
HELM = "/usr/local/bin/helm"
namespace = get_environment_variable_value('EIC_NAMESPACE')


def load_kube_configuration():
    try:
        config.load_incluster_config()
    except client.exceptions.ApiException as e:
        LOG.error(f"KPI Metrics: Failed to load kubernetes configuration, See detailed error: {e}")


def execute_command(cmd, pwd=None):
    rc = -1
    stdout = stderr = ""
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=pwd)
        stdout, stderr = process.communicate()
        rc = process.returncode

        return stdout, stderr, rc
    except subprocess.SubprocessError as e:
        LOG.error(f"Command: {cmd} execution failed due to Exception {e}")
        LOG.error(f'Error: {stderr}')
        return stdout, stderr, rc


def get_helm_release_list():
    cmd = f"{HELM} ls --all --short --namespace {namespace} | grep 'eric-*' |" \
          f" grep -v 'secret-eric'"
    release_list_output = execute_command(cmd, os.getcwd())[0].decode('utf-8')
    if not release_list_output:
        LOG.error(f"KPI Metrics: Helm release list command failed. Command executed: {cmd}")
        return []
    return release_list_output.strip().split()


def get_rel_deployments_data(rel):
    rel_deployments_data_list = []
    api = client.AppsV1Api()
    try:
        deploy_list_obj = api.list_namespaced_deployment(namespace,
                                                         label_selector=f"app.kubernetes.io/instance={rel}")
    except client.ApiException as e:
        LOG.debug(f"Getting deployments with release label failed. Error: {e}")
        return rel_deployments_data_list

    name_list = [i.metadata.name for i in deploy_list_obj.items]
    for name in name_list:
        try:
            dep_status_def = api.read_namespaced_deployment_status(name, namespace).status
            total_dep_replicas = dep_status_def.replicas
            avail_dep_replicas = dep_status_def.available_replicas
            rel_deployments_data_list.append({
                "deployment_name": name,
                "deployment_replicas": str(total_dep_replicas),
                "deployment_replicas_available": str(avail_dep_replicas),
                "deployment_availability": 1 if total_dep_replicas == avail_dep_replicas else 0
            })
        except (client.ApiException, KeyError) as e:
            LOG.debug(f"Fetching deployment detail failed for Deployment: {name}. Error: {e}")
            continue

    return rel_deployments_data_list


def get_rel_sts_data(rel):
    rel_sts_data_list = list()
    api = client.AppsV1Api()
    try:
        sts_list_obj = api.list_namespaced_stateful_set(namespace,
                                                        label_selector=f"app.kubernetes.io/instance={rel}")
    except client.ApiException as e:
        LOG.debug(f"Getting STS with release label failed. Error: {e}")
        return rel_sts_data_list

    name_list = [i.metadata.name for i in sts_list_obj.items]
    for name in name_list:
        try:
            sts_status_def = api.read_namespaced_stateful_set_status(name, namespace).status
            total_sts_replicas = sts_status_def.replicas
            avail_sts_replicas = sts_status_def.available_replicas
            rel_sts_data_list.append({
                "sts_name": name,
                "sts_replicas": str(total_sts_replicas),
                "sts_replicas_available": str(avail_sts_replicas),
                "sts_availability": 1 if total_sts_replicas == avail_sts_replicas else 0
            })
        except (client.ApiException, KeyError) as e:
            LOG.debug(f"Fetching STS detail failed for STS: {name}. Error: {e}")
            continue

    return rel_sts_data_list


def _get_pod_container_up_count(pod, total):
    count = 0
    for i in range(0, total):
        if pod.status.container_statuses[i].state.running is not None:
            count += 1

    return count


def get_rel_pod_data(rel):
    rel_pod_data_list = list()
    api = client.CoreV1Api()
    try:
        pod_list_obj = api.list_namespaced_pod(namespace, label_selector=f"app.kubernetes.io/instance={rel}")
    except client.ApiException as e:
        LOG.debug(f"Getting pods with release label failed. Error: {e}")
        return rel_pod_data_list

    name_list = [i.metadata.name for i in pod_list_obj.items]
    for pod in name_list:
        try:
            pod_def = api.read_namespaced_pod_status(pod, namespace)
            dep_sts_name = pod_def.metadata.labels['app.kubernetes.io/name']
            state = pod_def.status.phase
            container_count = len(pod_def.status.container_statuses)
            container_up_count = _get_pod_container_up_count(pod_def, container_count)
            pod_restart_count = sum(
                [pod_def.status.container_statuses[i].restart_count for i in range(0, container_count)])
            pod_availability = 1 if state == 'Running' and container_count == container_up_count else 0

            rel_pod_data_list.append({
                "pod_name": pod,
                "deployment_sts_name": str(dep_sts_name),
                "pod_current_state": state,
                "pod_restart_count": str(pod_restart_count),
                "pod_container_count": str(container_count),
                "pod_container_up_count": str(container_up_count),
                "pod_availability": pod_availability
            })
        except (client.ApiException, KeyError) as e:
            LOG.debug(f"Fetching pod detail failed for pod: {pod}. Error: {e}")
            continue

    return rel_pod_data_list


def get_release_data(release):
    rel_data_dict = {}
    deployment_key = 'deployments'
    pod_key = 'pods'
    sts_key = 'sts'
    rel_data_dict[deployment_key] = get_rel_deployments_data(release)
    rel_data_dict[pod_key] = get_rel_pod_data(release)
    rel_data_dict[sts_key] = get_rel_sts_data(release)

    return rel_data_dict


def get_eic_version():
    eic_ver = ""
    api = client.CoreV1Api()
    try:
        eic_ver = api.read_namespace_status(namespace).metadata.annotations['idunaas/installed-helmfile']
    except (client.ApiException, KeyError) as e:
        LOG.error(f"KPI Metrics: Failed fetching EIC Version for namespace: {namespace}. Error: {e}")
        return eic_ver

    return eic_ver


def get_all_release_data_list(release_list):
    resource_dict = dict()
    for release in release_list:
        resource_dict[release] = get_release_data(release)

    return resource_dict


def fetch_kpi_data():
    kpi_dict = dict()
    helm_release_list = get_helm_release_list()
    if not helm_release_list:
        return kpi_dict
    try:
        config.load_incluster_config()
    except client.exceptions.ApiException as e:
        LOG.error(f"KPI Metrics: Failed to load kubernetes configuration, See detailed error: {e}")
        return kpi_dict

    kpi_dict['namespace'] = namespace
    kpi_dict['eic_version'] = get_eic_version()
    kpi_dict['releases'] = get_all_release_data_list(helm_release_list)

    return kpi_dict
