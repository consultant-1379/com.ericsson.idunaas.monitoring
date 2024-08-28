"""
Querys AWS Cost Management to expose AWS Daily,Montly billings
"""

# GENERIC IMPORT #####
from prometheus_client import Gauge, Enum, start_http_server
import boto3
from datetime import datetime, timedelta, date
import time
import logging
import json
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)



class AwsMetrics:

    def __init__(self):

        self.polling_interval_seconds   = int(self.get_environment_variable_value('POLLING_INTERVAL_SECONDS'))
        self.deployment_type            = str.lower(self.get_environment_variable_value('DEPLOYMENT_TYPE'))
        self.bucket_name  = self.get_environment_variable_value('BUCKET_NAME') if self.deployment_type == "public" else None
        self.aws_client = boto3.client('ce') if self.deployment_type =='private' else None

        # Prometheus metrics to collect
        self.g_cost = Gauge('aws_daily_usage_costs', 'Today daily costs from AWS')
        self.g_prev_month = Gauge('aws_last_month_usage_costs', "Previous month costs from AWS")
        self.g_month = Gauge('aws_month_usage_costs', "Current month  usage costs from AWS")
        self.health = Enum("app_health", "Health", states=["healthy", "unhealthy"])

    def get_environment_variable_value(self,var_name):
        return os.environ[var_name] if var_name in os.environ else None

    def environment_variable_is_true(self,var_name):
        return bool(var_name in os.environ and os.environ[var_name].lower() == 'true')


    def run_metrics_loop(self):
        if  'public'    == self.deployment_type:
            while True:
                s3_path = 'cost-explorer.json'
                s3      = boto3.resource("s3")
                self.s3Object = s3.Object(self.bucket_name, s3_path)
                cost_data = json.loads(self.s3Object.get()['Body'].read().decode('utf-8'))
                logging.info("Updated AWS Daily costs: " + str(cost_data['aws_daily_cost']))
                self.g_cost.set(cost_data['aws_daily_cost'])
                logging.info("Updated AWS Current Month costs: " + str(cost_data['aws_current_month_cost']))
                self.g_month.set(cost_data['aws_current_month_cost'])
                logging.info("Updated AWS Previous Month costs: " + str(cost_data['aws_prev_month_cost']))
                self.g_prev_month.set(cost_data['aws_prev_month_cost'])
                time.sleep(self.polling_interval_seconds)

        elif 'private'    ==  self.deployment_type:
            while True:
                self.aws_daily_cost()
                self.aws_prev_month_cost()
                self.aws_current_month_cost()
                time.sleep(self.polling_interval_seconds)

    def aws_daily_cost(self):
        logging.info('Calculating daily usage costs')
        yesterday = datetime.today() - timedelta(days=1)
        before_yesterday = datetime.today() - timedelta(days=2)
        r = self.aws_client.get_cost_and_usage(
            TimePeriod={
                'Start': before_yesterday.strftime("%Y-%m-%d"),
                'End':  yesterday.strftime("%Y-%m-%d")
            },
            Granularity="DAILY",
            Metrics=["UnblendedCost"]
        )
        daily_cost = r["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
        logging.info("Updated AWS Daily costs: %s" %(daily_cost))
        self.g_cost.set(float(daily_cost))


    def aws_current_month_cost(self):
        first_date_current_month = datetime.today().replace(day=1)
        now = datetime.now()
        if now.date() > first_date_current_month.date():
            r = self.aws_client.get_cost_and_usage(
                TimePeriod={
                    'Start': first_date_current_month.strftime("%Y-%m-%d"),
                    'End':  now.strftime("%Y-%m-%d")
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"]
            )
            current_month_cost = r["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
        else:
            current_month_cost = 0
        logging.info("Updated AWS Current month costs: %s" %(current_month_cost))
        self.g_month.set(float(current_month_cost))


    def aws_prev_month_cost(self):
        last_day_of_previous_month = date.today().replace(day=1) - timedelta(days=1)
        first_day_of_previous_month =  date.today().replace(day=1) - timedelta(days=last_day_of_previous_month.day)
        first_date_current_month = date.today().replace(day=1)
        r = self.aws_client.get_cost_and_usage(
            TimePeriod={
                'Start': first_day_of_previous_month.strftime("%Y-%m-%d"),
                'End':  first_date_current_month.strftime("%Y-%m-%d")
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"]
        )
        cost = r["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
        logging.info("Updated AWS Last Month costs: %s" %(cost))
        self.g_prev_month.set(float(cost))




def main():

    aws_metrics = AwsMetrics()

    start_http_server(8080)
    logger.info("Starting HTTP Server")
    aws_metrics.run_metrics_loop()


if __name__ == "__main__":
    main()

