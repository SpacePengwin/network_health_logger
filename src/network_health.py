import argparse
import os
from lib.logger import generate_logger
from lib import datadog, iperf, ping
from sys import exit

logger = generate_logger("network_health")

USAGE_MESSAGE = """This is a command line tool to measure and log ping(latency & packet_loss) metrics as well as 
iperf(bandwidth) metrics. This can be used to target a remote or local host. The results for each test will be posted to
Datadog for monitoring.

You must have $DATADOG_API_KEY set as an environment variable to authenticate with your Datadog account.
`export DATADOG_API_KEY=$API_KEY`

Specify `-h` to see available tests
"""


def parse_opts():
    parser = argparse.ArgumentParser(usage=USAGE_MESSAGE)
    parser.add_argument("--iperf-host", dest="iperf_host", required=False, default=None,
                        help="Specify a local host address to run an iperf test against. If not specified, the test "
                             "will not run.")
    parser.add_argument("--remote-iperf-host", dest="remote_iperf_host", required=False, default=None,
                        help="Specify a remote host address to run an iperf test against. If not specified, the test "
                             "will not run.")
    parser.add_argument("--ping-host", dest="ping_host", required=False, default=None,
                        help="Specify a local host address to run a ping test against. If not specified, the test will "
                             "not run.")
    parser.add_argument("--remote-ping-host", dest="remote_ping_host", required=False, default=None,
                        help="Specify a remote host address to run a ping test against. If not specified, the test "
                             "will not run.")
    parser.add_argument("--number-of-packets", dest="number_of_packets", required=False, default=100,
                        help="Specify a number of packets to use for the ping tests. This value is the same for both "
                             "local and remote ping tests. Default = 100 packets")
    parser.add_argument("--disable-datadog-submit", default=False, dest="disable_datadog_submit",
                        action="store_true", help="Specify this argument to bypass submitting the results to Datadog."
                                                  " Default = False")
    parser.add_argument("--local-iperf-port", dest="local_iperf_port", default=None,
                        help="Specify the port to use for the local iperf test. Default = None")
    parser.add_argument("--remote-iperf-port", dest="remote_iperf_port", default=None,
                       help="Specify the port to use for the remote iperf test. Default = None")

    return parser.parse_args()


if __name__ == "__main__":
    dd_client = None
    results = {}
    DATADOG_API_KEY = os.getenv("DATADOG_API_KEY", None)

    args = parse_opts()

    if not args.disable_datadog_submit:
        if DATADOG_API_KEY is None:
            logger.error(f"Failed to find $DATADOG_API_KEY environment variable. Exiting..")
            exit(255)

    specified_tests = [test for test in [args.iperf_host, args.remote_iperf_host, args.ping_host, args.remote_ping_host]
                       if test is not None]  # Count the number of test that are to run.
    if len(specified_tests) == 0:
        print(USAGE_MESSAGE)
        exit(1)

    if not args.disable_datadog_submit:
        logger.info(f"Creating Datadog client.")
        dd_client = datadog.DatadogClient(DATADOG_API_KEY)
        logger.info("Validating provided credentials...")
        dd_client.validate_credentials()
        logger.info("Successfully validated provided Datadog credentials.")
    else:
        logger.info("Datadog submission is disabled.")

    if args.ping_host is not None:
        logger.info("Starting local ping test...")
        ping_results = ping.run_ping(args.ping_host, number_of_packets=args.number_of_packets)
        if dd_client is not None:
            dd_client.submit_ping_network_health(ping_results)

    if args.remote_ping_host is not None:
        logger.info(f"Starting remote ping test...")
        remote_ping_results = ping.run_ping(args.remote_ping_host, number_of_packets=args.number_of_packets)
        if dd_client is not None:
            dd_client.submit_ping_network_health(remote_ping_results, local=False)

    if args.iperf_host is not None:
        logger.info("Starting local iperf test...")
        local_iperf_results = iperf.run_iperf(args.iperf_host, port=args.local_iperf_port)
        if dd_client is not None:
            dd_client.submit_bandwidth_data(local_iperf_results)

    if args.remote_iperf_host is not None:
        logger.info("Starting remote iperf test...")
        remote_iperf_results = iperf.run_iperf(args.remote_iperf_host, port=args.remote_iperf_port)
        if dd_client is not None:
            dd_client.submit_bandwidth_data(remote_iperf_results, local=False)

    logger.info("Completed.")
