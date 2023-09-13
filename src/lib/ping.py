import subprocess
import re
import platform
import logging


class PingExecutionFailed(Exception):
    """Raised when running the ping process fails."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedToParsePing(Exception):
    """Raised when running the ping process fails."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


logger = logging.getLogger("network_health")

CURRENT_PLATFORM = platform.system()
logger.info(f"Operating System: {CURRENT_PLATFORM}")


def run_ping(target: str, number_of_packets: int = 100):
    """
    The run_ping function takes a target and an optional number of packets to send.
    It then runs the ping command on the target with the specified number of packets,
    and returns a dictionary containing information about packet loss, minimum latency,
    average latency, max latency and standard deviation in latencies.

    :param target: str: Specify the target of the ping
    :param number_of_packets: int: Specify the number of packets to send
    :return: A dictionary with the following keys:
        (packet_loss, minimum_latency, average_latency, max_latency, standard_deviation_latency)
    """
    logger.info("Determining platform...")
    if CURRENT_PLATFORM == "Windows":
        command = ["ping", target, "-n", str(number_of_packets)]
    else:
        command = ["ping", target, "-c", str(number_of_packets)]
    logger.info(f"Platform is: {CURRENT_PLATFORM} running ping against target: {target} for {number_of_packets} "
                f"packets...")

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    logger.info("Completed ping process, parsing output...")
    logger.debug(f"Ping output:\n {stdout}")


    if CURRENT_PLATFORM != "Windows":
        pattern = r"\s*(\d*|\d*.\d*)%.*\n.*min\/avg\/max\/.*dev\s*=\s*(\d*.\d*|\d*)\/(\d*.\d*|\d*)\/(\d*.\d*|\d*)\/(\d*.\d*|\d*)\s*ms"
    else:
        pattern = r"\s*\((\d*|\d*.\d*)%.*Minimum\s*=\s*(\d*|\d*.\d*)ms.*Maximum\s*=\s*(\d*|\d*.\d*)ms.*Average\s*=\s*(\d*|\d*.\d*)ms"


    # Search for the pattern in the text, ignoring whitespace and line breaks
    match = re.search(pattern, stdout, re.DOTALL | re.IGNORECASE)

    if match:
        logger.info("Found pattern matches within ping results!")
        packet_loss = match.group(1)
        min_latency = match.group(2)
        avg_latency = match.group(3)
        max_latency = match.group(4)
        stddev_latency = match.group(5)

        results = {
            "packet_loss": packet_loss,
            "minimum_latency": min_latency,
            "average_latency": avg_latency,
            "max_latency": max_latency,
            "standard_deviation_latency": stddev_latency
        }

        logger.info("Results:")
        for metric, value in results.items():
            unit = "millisecond(s)"
            if metric == "packet_loss":
                unit = "%"
            logger.info(f"{metric}: {value} {unit}")
        return results
    else:
        logger.error("Failed to find pattern matches within ping results.")
        raise FailedToParsePing()
