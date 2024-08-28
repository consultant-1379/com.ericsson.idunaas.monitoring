import configparser
from prometheus_client.core import GaugeMetricFamily
from prometheus_client import start_http_server
from kubernetes import client
from kubernetes import config as kube_config
import pytest
import logsystem
import evnfm_uiavailability
import exporter


def test_custom_collector_init():
    """Test the initialization of the CustomCollector class"""
    test_config_path = "test_config.ini"  # Update this with the path to your test configuration file
    custom_collector = exporter.CustomCollector(test_config_path)
    assert custom_collector is not None


def test_custom_collector_collect(mocker):
    """Test the collection of metrics from the CustomCollector class"""
    test_config_path = "test_config.ini"  # Update this with the path to your test configuration file
    mocker.patch.object(
        configparser,
        'ConfigParser',
        return_value=mocker.Mock())
    mocker.patch.object(logsystem, 'get_logger', return_value=mocker.Mock())

    # Updated health_status dictionary to match the expected structure
    health_status_mock = {
        "overall_status": 1,
        "hostname": "example.com",
        "tcp_check_status": 1,
        "http_check_status": 1,
        "login_check_status": 1
    }

    mocker.patch.object(
        evnfm_uiavailability,
        'evnfm_ui_availability',
        return_value=health_status_mock)
    mocker.patch.object(GaugeMetricFamily, 'add_metric', return_value=None)

    custom_collector = exporter.CustomCollector(test_config_path)
    result = list(custom_collector.collect())

    assert result is not None


def test_start_http_server(mocker):
    """Test the start of the HTTP server for Prometheus"""
    mocker.patch('prometheus_client.start_http_server', return_value=None)
    # mocker.patch.object(start_http_server, 'start_http_server', return_value=None)
    start_http_server(8000)
    assert True


def test_kube_config(mocker):
    """Test the loading of the Kubernetes configuration"""
    mocker.patch.object(kube_config, 'load_kube_config', return_value=None)
    kube_config.load_kube_config()
    assert kube_config.load_kube_config.called

def test_return_metric():
    """Test return metric"""
    environment = "test"
    name = "evnfm_ui"
    health_status = {
        "overall_status": 1,
        "hostname": "example.com",
        "tcp_check_status": 1,
        "http_check_status": 1,
        "login_check_status": 1
    }

    result = exporter.return_metric(environment, name, health_status)

    assert isinstance(result, exporter.GaugeMetricFamily)


def test_return_metric_generic():
    """Test return metric generic"""
    name = "test_metric"
    value = 1
    documentation = "Test metric"
    sub_metric_labels = ["label1", "label2"]
    sub_metric_values = ["value1", "value2"]

    result = exporter.return_metric_generic(
        name, value, documentation, sub_metric_labels, sub_metric_values)

    assert isinstance(result, exporter.GaugeMetricFamily)
