import requests
import logging
from socket import gethostname
import time
import json

logger = logging.getLogger("network_health")

METRIC_TYPE_COUNT = 1  # Datadog enum for metric type of `count`
METRIC_TYPE_RATE = 2  # Datadog enum for metric type of `rate`


def generate_network_data_body(data: dict, hostname: str, test_type: str):
    """
    The generate_network_data_body function takes in a dictionary of data, the hostname, and the test type.
    It then creates a timestamp for each item in the dictionary and appends it to an empty list.
    The function returns a series of points with timestamps.

    :param data: dict: Pass the data collected from the network tests
    :param hostname: str: Identify the hostname of the device
    :param test_type: str: Determine what type of test is being run
    :return: A formatted dictionary in a format the Datadog metrics endpoint requires
    """
    metric_units = {
        "transfer_value": "megabyte",
        "bandwidth_value": "megabyte",
        "interval_value": "megabyte",
        "packet_loss": "percent",
        "minimum_latency": "millisecond",
        "average_latency": "millisecond",
        "max_latency": "millisecond",
        "standard_deviation_latency": "millisecond"
    }

    metric_types = {
        "transfer_value": METRIC_TYPE_RATE,
        "bandwidth_value": METRIC_TYPE_RATE,
        "interval_value": METRIC_TYPE_RATE,
        "packet_loss": METRIC_TYPE_COUNT,
        "minimum_latency": METRIC_TYPE_RATE,
        "average_latency": METRIC_TYPE_RATE,
        "max_latency": METRIC_TYPE_RATE,
        "standard_deviation_latency": METRIC_TYPE_RATE
    }

    timestamp = int(time.time())
    series_points = []
    for key, value in data.items():
        unit = metric_units[key]
        metric_type = metric_types[key]
        each_item = {
            "metric": f"network_health.{test_type}.{key}",
            "resources": [
                {
                    "name": hostname,
                    "type": "host"
                }
            ],
            "type": metric_type,
            "unit": unit,
            "points": [
                {
                    "timestamp": timestamp,
                    "value": value
                }
            ],
        }
        series_points.append(each_item)
    return {"series": series_points}


class DatadogAuthenticationError(Exception):
    """Raised when the provided credentials fail to authenticate with Datadog."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DatadogNotAuthenticated(Exception):
    """Raised when attempting to access Datadog without being authenticated."""

    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class DatadogFailedMetricsUpdate(Exception):
    """Raised when updating metrics in Datadog fails."""

    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class DatadogClient:
    def __init__(self, api_key, host=gethostname()):
        logger.info(f"Initializing Datadog Client as host={host}")
        self.base_url = "https://api.datadoghq.com/api"
        self.api_key = api_key
        self.host = host
        self.base_headers = {"DD-API-KEY": self.api_key}
        self.credentials_validated = False

    def validate_credentials(self):
        """
        The validate_credentials function is used to validate the credentials provided by the user. It does this by
        making a GET request to Datadog's /v1/validate endpoint, which returns a 200 status code if successful. If it
        fails, it raises an exception.

        :param self: Refer to the instance of the class
        :return: True if the credentials are valid, and raises an exception otherwise
        """
        url = f"{self.base_url}/v1/validate"
        headers = dict(self.base_headers)
        headers.update({"Accept": "application/json"})
        response = requests.get(url, headers=headers)
        if response.ok:
            self.credentials_validated = True
        else:
            raise DatadogAuthenticationError(
                f"Failed to validate Datadog credentials, status code: {response.status_code} || Error message: {response.reason}")

    def handle_metric_submission(self, data):
        """
        The handle_metric_submission function is responsible for sending the metrics to Datadog.
        It takes a list of metric objects as input, and returns True if the submission was successful.
        If it fails, it raises an exception.

        :param self: Refer to the current instance of a class
        :param data: Pass the data to be sent to datadog
        :return: True if the metrics are successfully submitted to datadog
        """
        if not self.credentials_validated:
            raise DatadogNotAuthenticated()
        url = f"{self.base_url}/v2/series"
        headers = dict(self.base_headers)
        headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key
        })
        data = json.dumps(data)
        response = requests.post(url, headers=headers, data=data)
        if response.ok:
            return True
        else:
            logger.error(f"Failed to update Datadog with metrics, error: {response.reason}")
            raise DatadogFailedMetricsUpdate()

    def submit_ping_network_health(self, data: dict, local: bool = True):
        """
        The submit_ping_network_health function is used to submit a ping test result to the network health endpoint.
            The function takes two arguments: data and local. Data is a dictionary containing the following keys: -

        :param self: Bind the method to an object
        :param data: dict: Pass in the data that is to be sent
        :param local: bool: Determine if the ping is local or remote and sets the metric name based on this
        """
        if local:
            test_type = "ping_local"
        else:
            test_type = "ping_remote"
        logger.info("Generating data body for ping test...")
        data = generate_network_data_body(data, self.host, test_type=test_type)
        logger.info(f"Generated ping data body, submitting to endpoint as {test_type}")
        self.handle_metric_submission(data)
        logger.info(f"Successfully submitted metric data for ping as {test_type}")

    def submit_bandwidth_data(self, data: dict, local: bool = True):

        """
        The submit_bandwidth_data function is used to submit bandwidth data to the network_health endpoint.
            The function takes a dictionary of data as an argument, and submits it in JSON format.
            The function also takes a boolean value that determines whether the test was local or remote.

        :param self: Bind the method to an object
        :param data: dict: Pass in the data that is to be submitted
        :param local: bool: Determine whether the test is local or remote
        :return: The handle_metric_submission function
        """
        if local:
            test_type = "bandwidth_local"
        else:
            test_type = "bandwidth_remote"
        logger.info("Generating data body for bandwidth test...")
        data = generate_network_data_body(data, self.host, test_type=test_type)
        logger.info(f"Generated bandwidth data body, submitting to endpoint as {test_type}")
        self.handle_metric_submission(data)
        logger.info(f"Successfully submitted metric data for bandwidth as {test_type}")
