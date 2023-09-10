import subprocess
import re
import platform
import logging


class IperfExecutionFailed(Exception):
    """Raised when running the ping process fails."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedToParseIperfResults(Exception):
    """Raised when running the ping process fails."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


logger = logging.getLogger("network_health")

CURRENT_PLATFORM = platform.system()
logger.info(f"Operating System: {CURRENT_PLATFORM}")


def run_iperf(target: str, port: int=None):
    """
    The run_iperf function runs the iperf command on a target host and returns the transfer value and bandwidth value.

    :param target: str: Specify the target ip address
    :return: A dictionary with two keys:
    """

    def validate_iperf_results(match_value: re.Match):
        if match_value is not None:
            return match_value.group(1)
        logger.error("Failed to find march on pattern!")
        raise FailedToParseIperfResults

    logger.info(f"Starting iperf process with target: {target}...")
    if CURRENT_PLATFORM == "Windows":
        command = ["iperf2", "-c", target, "-w", "128K", "-f", "M"]
    else:
        command = ["iperf", "-c", target, "-f", "M"]
    if port is not None:
        logger.info(f"Port is specified, appending: `-p {port}`")
        command.extend(["-p", port])

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    logger.info("Completed iperf process, parsing output...")
    logger.debug(f"iperf output:\n {stdout}")

    transfer_pattern = r"(\d+) MBytes"
    bandwidth_pattern = r"(\d+) MBytes\/sec"
    interval_pattern = r"-(.*\d) sec"

    transfer_match = re.search(transfer_pattern, stdout)
    bandwidth_match = re.search(bandwidth_pattern, stdout)
    interval_match = re.search(interval_pattern, stdout)

    transfer_value = validate_iperf_results(transfer_match)
    bandwidth_value = validate_iperf_results(bandwidth_match)
    interval_value = validate_iperf_results(interval_match)

    logger.info("Found pattern matches from iperf output!")

    results = {
        "transfer_value": transfer_value,
        "bandwidth_value": bandwidth_value,
        "interval_value": interval_value
    }

    logger.info("Results:")

    for metric, value in results.items():
        unit = "megabyte(s)"
        if metric == "interval_value":
            unit = "second(s)"
        logger.info(f"{metric}: {value} {unit}")

    return results
