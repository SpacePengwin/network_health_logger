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
    print(stdout)

    logger.info("Completed iperf process, parsing output...")

    transfer_pattern = r"sec\s*(\d*.\d*) MBytes"
    bandwidth_pattern = r"MBytes\s* (\d*.\d*)\s*MBytes\/sec"
    interval_pattern = r"-(.*\d) sec"

    pattern = r"]\s*0.00-(\d*.\d*) sec\s*(\d*)\s*MBytes\s*(\d*.\d*) \s*MBytes"

    match = re.search(pattern, stdout)
    
    if match:
        transfer_match = match.group(1)
        bandwidth_match = match.group(2)
        interval_match = match.group(3)
    else:
        logger.error(f"Failed to find regex match from iperf results, stdout:\n {stdout}")
        exit(1)

    logger.info("Found pattern matches from iperf output!")

    results = {
        "transfer_value": transfer_match,
        "bandwidth_value": bandwidth_match,
        "interval_value": interval_match
    }

    logger.info("Results:")

    for metric, value in results.items():
        unit = "megabyte(s)"
        if metric == "interval_value":
            unit = "second(s)"
        logger.info(f"{metric}: {value} {unit}")

    return results
