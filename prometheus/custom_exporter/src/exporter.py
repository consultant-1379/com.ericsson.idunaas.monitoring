"""                                                           <
This will initialize prometheus client, Gauges,               <
start the http server and invoke other metrics collector scri <
evnfm_uiavailability to get the metrics etc.                  <
"""
import os
import time
import apps_metric
import enm_uiavailability
import eocm_serviceavailability
import eocm_uiavailability
import evnfm_uiavailability
import helm_stats
import logsystem
import utils

from configparser import ConfigParser, NoOptionError
from kubernetes import client
from kubernetes import config as kube_config
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from kpi_metrics import fetch_kpi_data

LOG = logsystem.get_logger(__name__)


class CustomCollector:
    """Custom collector collects metrics
    from other systems and sets the metric"""

    def __init__(self, config_path):
        self.config = ConfigParser()
        try:
            self.config.read(config_path)
            LOG.debug('Config Sections: %s', self.config.sections())
        except:
            LOG.error(f'Error while reading config file {config_path}', exc_info=True)

    def collect(self):
        """
        This method will be invoked by other subsystem health check
        script to export their health status on to prometheus metric
        :return: Yields a gauge metric
        """
        LOG.info('Collection of metrics started')
        for environment in self.config.sections():
            LOG.info(f'Subsystems configuration found for {environment}.')
            try:
                subsystems_monitored = self.config.get(environment, "SUBSYSTEM_MONITORED")
                subsystems_monitored_list = subsystems_monitored.split(",")
            except NoOptionError:
                subsystems_monitored_list = ""
                LOG.error(f"No subsystems to monitor for the environment {environment}.", exc_info=True)
                LOG.error("SUBSYSTEM_MONITORED config key missing")

            if "evnfm_ui" in subsystems_monitored_list:
                try:
                    evnfm_ui_url = self.config.get(environment, "EVNFMUI_URL")
                    evnfm_ui_user = self.config.get(environment, "EVNFMUI_USER")
                    evnfm_ui_passwd = self.config.get(environment, "EVNFMUI_PASSWD")
                except NoOptionError:
                    evnfm_ui_url, evnfm_ui_user, evnfm_ui_passwd = ("",) * 3
                    LOG.error(f"Missing subsystems config params for the environment {environment}.", exc_info=True)
                    LOG.error("EVNFMUI_URL or EVNFMUI_USER or EVNFMUI_PASSWD config key missing")
                health_status = evnfm_uiavailability.evnfm_ui_availability(evnfm_ui_url,
                                                                           evnfm_ui_user,
                                                                           evnfm_ui_passwd)
                yield return_metric(environment, 'evnfm_ui', health_status)
            else:
                LOG.debug('evnfm_ui monitoring is disabled')

            if "enm_ui" in subsystems_monitored_list:
                try:
                    enm_ui_url = self.config.get(environment, "ENMUI_URL")
                    enm_ui_user = self.config.get(environment, "ENMUI_USER")
                    enm_ui_passwd = self.config.get(environment, "ENMUI_PASSWD")
                except NoOptionError:
                    enm_ui_url, enm_ui_user, enm_ui_passwd = ("",) * 3
                    LOG.error(f"Missing subsystems config params for the environment {environment}.", exc_info=True)
                    LOG.error("ENMUI_URL or ENMUI_USER or ENMUI_PASSWD config key missing")
                health_status = enm_uiavailability.enm_ui_availability(enm_ui_url,
                                                                       enm_ui_user,
                                                                       enm_ui_passwd)
                yield return_metric(environment, 'enm_ui', health_status)
            else:
                LOG.debug('enm_ui monitoring is disabled')

            if "eocm_ui" in subsystems_monitored_list:
                try:
                    eocm_ui_url = self.config.get(environment, "EOCMUI_URL")
                    eocm_ui_user = self.config.get(environment, "EOCMUI_USER")
                    eocm_ui_passwd = self.config.get(environment, "EOCMUI_PASSWD")
                except NoOptionError:
                    eocm_ui_url, eocm_ui_user, eocm_ui_passwd = ("",) * 3
                    LOG.error(f"Missing subsystems config params for the environment {environment}.", exc_info=True)
                    LOG.error("EOCMUI_URL or EOCMUI_USER or EOCMUI_PASSWD config key missing")
                health_status = eocm_uiavailability.eocm_ui_availability(eocm_ui_url,
                                                                         eocm_ui_user,
                                                                         eocm_ui_passwd)
                yield return_metric(environment, 'eocm_ui', health_status)
            else:
                LOG.debug('eocm_ui monitoring is disabled')

            if "eocm_sa" in subsystems_monitored_list:
                try:
                    eocm_sa_host = self.config.get(environment, "EOCM_SA_HOST")
                    eocm_sa_user = self.config.get(environment, "EOCM_SA_USER")
                    eocm_sa_passwd = self.config.get(environment, "EOCM_SA_PASSWD")
                    eocm_sa_cmd = self.config.get(environment, "EOCM_SA_COMMAND")
                except NoOptionError:
                    eocm_sa_host, eocm_sa_user, eocm_sa_passwd, eocm_sa_cmd = ("",) * 4
                    LOG.error(f"Missing subsystems config params for the environment {environment}.", exc_info=True)
                    LOG.error("EOCM_HOST or EOCM_USER or EOCM_PASSWD or EOCM_COMMAND config key missing")
                health_status = eocm_serviceavailability.eocm_service_availability(eocm_sa_host,
                                                                                   eocm_sa_user,
                                                                                   eocm_sa_passwd, eocm_sa_cmd)
                yield return_metric(environment, 'eocm_sa', health_status)
            else:
                LOG.debug('eocm_sa monitoring is disabled')
        else:
            LOG.info('Subsystems monitoring is disabled')

        if utils.environment_variable_is_true('APPS_ENABLED'):
            LOG.info('rApps monitoring is enabled')
            apps_url = utils.get_environment_variable_value('APPS_URL')
            apps_user = utils.get_environment_variable_value('APPS_USER')
            apps_passwd = utils.get_environment_variable_value('APPS_PASSWD')
            apps_statistic = apps_metric.apps_metric(apps_url, apps_user, apps_passwd)
            yield return_metric_generic(**apps_statistic)
        else:
            LOG.info('rApps monitoring is disabled')

        # Read helmfile and chartversions from eric-installed-application configmap from eic_namespace
        if utils.environment_variable_is_true('MONITOR_CHART_VERSIONS'):
            eic_namespace = utils.get_environment_variable_value('EIC_NAMESPACE')
            LOG.info(f'Helm stats monitored for namespace {eic_namespace}')
            try:
                # kube_config.load_kube_config()
                # Enable to read connect kube cluster inside POD
                kube_config.load_incluster_config()
            except:
                LOG.error("Unable to load kube configuration", exc_info=True)
            client_api = client.CoreV1Api()
            if not eic_namespace:
                LOG.error("Empty Namespace in config.ini")
            else:
                installed_versions = helm_stats.read_installed_helm_cm(eic_namespace, client_api)
                chart_guage = GaugeMetricFamily('eric_installed_apps_chart_version', 'Version of installed chart',
                                                labels=['name', 'version', 'namespace'])
                for csar in installed_versions['csar']:
                    chart_guage.add_metric([csar['name'], csar['version']], True)
                yield chart_guage
                # Helmfile version
                helm_version = installed_versions['helmfile']
                yield return_metric_generic('eric_installed_apps_helmfile_version', True, 'Installed Helm Version',
                                            sub_metric_labels=[helm_version['name'].replace('-', '_'), 'namespace'],
                                            sub_metric_values=[helm_version['release'], eic_namespace])
                # Deployment version
                yield return_metric_generic('eric_installed_apps_dep_mgr', True, 'Deployment Manager Version',
                                            sub_metric_labels=['version', 'namespace'],
                                            sub_metric_values=[installed_versions['deployment-manager'],
                                                               eic_namespace])
                # Tags
                app_tags = installed_versions['tags']
                gauge = GaugeMetricFamily('eric_installed_apps', 'Status of Installed APPs',
                                          labels=['app', 'namespace'])
                for app in app_tags:
                    gauge.add_metric([app, eic_namespace], app_tags[app])
                yield gauge
        else:
            LOG.info("Helm Stats monitoring disabled ")

        # Below section is to collect Data from EIC Deployments for KPI Analysis and Reporting
        if utils.environment_variable_is_true('KPI_COLLECTOR'):
            eic_namespace = utils.get_environment_variable_value('EIC_NAMESPACE')
            LOG.info(f'KPI Metrics: Starting Data collection for EIC Namespace: {eic_namespace}')
            kpi_data = fetch_kpi_data()
            if kpi_data:
                releases_data = kpi_data['releases']
                deployment_gauge = GaugeMetricFamily('eic_deployment_availability', 'EIC Deployment availability',
                                                     labels=utils.get_kpi_metric_keys('deployments'))
                sts_gauge = GaugeMetricFamily('eic_sts_availability', 'EIC STS availability',
                                                     labels=utils.get_kpi_metric_keys('sts'))
                pod_gauge = GaugeMetricFamily('eic_pod_availability', 'EIC Pod availability',
                                                     labels=utils.get_kpi_metric_keys('pods'))
                LOG.debug(f'KPI Metrics: Starting Data parsing into Prometheus Metrics')
                for release in releases_data:
                    release_deployment_list = releases_data[release]['deployments']
                    release_sts_list = releases_data[release]['sts']
                    release_pods_list = releases_data[release]['pods']

                    for deployment in release_deployment_list:
                        dep_values_list = [deployment[key] for key in utils.get_kpi_metric_keys('deployments')]
                        deployment_gauge.add_metric(dep_values_list, deployment['deployment_availability'])
                    for sts in release_sts_list:
                        sts_values_list = [sts[key] for key in utils.get_kpi_metric_keys('sts')]
                        sts_gauge.add_metric(sts_values_list, sts['sts_availability'])
                    for pod in release_pods_list:
                        pod_values_list = [pod[key] for key in utils.get_kpi_metric_keys('pods')]
                        pod_gauge.add_metric(pod_values_list, pod['pod_availability'])

                yield deployment_gauge
                yield sts_gauge
                yield pod_gauge
            else:
                LOG.error(f'KPI Metrics: No data returned from cluster')
        else:
            LOG.info(f'KPI Metrics Collection disabled')

        LOG.info('Collection of metrics finished')


def return_metric_generic(name, value, documentation, sub_metric_labels, sub_metric_values):
    gauge = GaugeMetricFamily(name, documentation, labels=sub_metric_labels)
    gauge.add_metric(sub_metric_values, value)
    return gauge


def return_metric(environment, name, health_status):
    """
    This method will be called by the collector and return the gauge value
    Args:
        environment: environment name from the config.ini
        name: Name of the subsystem
        health_status: Health status of the subsystem
    Returns:
        gauge
    """
    if name == "eocm_sa":
        return return_metric_generic(
            name=f"{environment}_{name}_health_status",
            value=health_status['overall_status'],
            documentation="Check status of service",
            sub_metric_labels=["hostname"],
            sub_metric_values=[health_status['hostname']]
        )
    else:
        return return_metric_generic(
            name=f"{environment}_{name}_health_status",
            value=health_status['overall_status'],
            documentation="Check status of service",
            sub_metric_labels=["hostname", "tcpcheck", "httpscheck", "logincheck"],
            sub_metric_values=[
                health_status['hostname'],
                health_status['tcp_check_status'],
                health_status['http_check_status'],
                health_status['login_check_status']
            ]
        )

# MAIN SCRIPT


if __name__ == '__main__':
    LOG.info(f'Current working directory: {os.getcwd()}')
    config_path = '/config/config.ini'
    if not os.path.exists(config_path):
        config_path = 'config.ini'
        if not os.path.exists(config_path):
            LOG.debug("config.ini not found neither in the current "
                      f"directory {os.getcwd()} nor in /config")

    start_http_server(8008)
    LOG.info("Starting HTTP Server on port 8008")
    REGISTRY.register(CustomCollector(config_path))
    while True:
        time.sleep(1)
