# network_health_logger
`network_health_logger` is a command line utility to measure ang log a device's network connection. This currently provides the following metrics for the host it runs on:  
1. Minimum Latency (milliseconds)
2. Maximum Latency (milliseconds)
3. Average Latency (milliseconds)
4. Standard Deviation Latency (milliseconds)
5. Packet Loss (percentage)
6. Bandwidth (megabyte)
7. Bandwidth Transfer Rate (megabyte/s)
8. Bandwidth Interval (seconds)

Each of these metrics can be tested against a local address or a remote address.

Each of these can be submitting to Datadog as a metric.

The goal is to allow this tool to run on as many hosts as possible with as little setup as neccessary. 

# Requirements
In order to use this tool, you must meet the following requirements:
1. `ping` must be installed and in PATH
2. `iperf` must be installed and in PATH
    1. Install `iperf` on Debian-based Linux distributions:
        ```
        sudo apt update && sudo apt install iperf -y
        ```
    2. Install `iperf` on RHEL-based distributions:
        ```
        sudo yum install iperf
        ```
    3. Install `iperf` on MacOS
        ```
        brew install iperf
        ```

3. `Python3.6+`
4. `requests` PyPi package
    1. ```
       pip3 install requests
       ``` 

# Installation
1. Clone the repository:
    ```
    $ git clone https://github.com/SpacePengwin/network_health_logger.git
    ```
2. Run the `network_health.py` file:
    ```
    $ python3 network_health_logger/src/network_health.py
    ```

# Usage
This tool will default to submitting all results to Datadog as metric values. This requires you to have your Datadog API key set as an environment variable:
```
$ export DATADOG_API_KEY=$API_KEY
```

Appending `--disable-datadog-submit` to the arguments removes the `$DATADOG_API_KEY` environment variable requirement to run the tool.


In order to run a test, you must specify the target host to run the test against. If you do not specify a host, the test will be skipped.

Arguments:
```
  --iperf-host IPERF_HOST
                        Specify a local host address to run an iperf test
                        against. If not specified, the test will not run.
  --remote-iperf-host REMOTE_IPERF_HOST
                        Specify a remote host address to run an iperf test
                        against. If not specified, the test will not run.
  --ping-host PING_HOST
                        Specify a local host address to run a ping test
                        against. If not specified, the test will not run.
  --remote-ping-host REMOTE_PING_HOST
                        Specify a remote host address to run a ping test
                        against. If not specified, the test will not run.
  --number-of-packets NUMBER_OF_PACKETS (optional)
                        Specify a number of packets to use for the ping tests.
                        This value is the same for both local and remote ping
                        tests. Default = 100 packets
  --disable-datadog-submit (optional)
                        Specify this argument to bypass submitting the results
                        to Datadog. Default = False
```


Example usage to run all tests:
```
$ python3 network_health_logger/src/network_health.py --iperf-host 192.168.1.2 --remote-iperf-host 35.35.35.35 --ping-host 192.168.1.1 --remote-ping-host 8.8.8.8
```

This will run a test to measure ping results from `192.168.1.1` (local) and `8.8.8.8` (remote). The ping metrics will measure:
1. Minimum Latency (milliseconds)
2. Maximum Latency (milliseconds)
3. Average Latency (milliseconds)
4. Standard Deviation Latency (milliseconds)
5. Packet Loss (percentage)

This will also run a test to measure the bandwidth from a local iperf server: `192.168.1.2` and a remote iperf server: `35.35.35.35`. The iperf metrics will measure:
1. Bandwidth (megabyte)
2. Bandwidth Transfer Rate (megabyte/s)
3. Bandwidth Interval (seconds)


The collected metrics will be printed to stdout for each test:
1. Ping results:
    ```
    2023-09-10 16:48:57,681 - network_health - INFO - [ping.py:run_ping:75] - Results:
    2023-09-10 16:48:57,681 - network_health - INFO - [ping.py:run_ping:80] - packet_loss: 0.0 %
    2023-09-10 16:48:57,681 - network_health - INFO - [ping.py:run_ping:80] - minimum_latency: 0.358 millisecond(s)
    2023-09-10 16:48:57,681 - network_health - INFO - [ping.py:run_ping:80] - average_latency: 0.471 millisecond(s)
    2023-09-10 16:48:57,681 - network_health - INFO - [ping.py:run_ping:80] - max_latency: 0.591 millisecond(s)
    2023-09-10 16:48:57,681 - network_health - INFO - [ping.py:run_ping:80] - standard_deviation_latency: 0.079 millisecond(s)
    ```

2. iperf results:
    ```
    2023-09-10 16:50:04,819 - network_health - INFO - [iperf.py:run_iperf:72] - Results:
    2023-09-10 16:50:04,819 - network_health - INFO - [iperf.py:run_iperf:78] - transfer_value: 1126 megabyte(s)
    2023-09-10 16:50:04,819 - network_health - INFO - [iperf.py:run_iperf:78] - bandwidth_value: 112 megabyte(s)
    2023-09-10 16:50:04,819 - network_health - INFO - [iperf.py:run_iperf:78] - interval_value: 10.04 second(s)
    ```


These results will also be submitted to Datadog as metrics. If you do not want to submit the metrics to Datadog, you can append the argument: `--disable-datadog-submit`.

As an example, if you wanted to run a `ping` test against a local address: `192.168.1.1` with only `10` packets transmitted and without submitting the results to Datadog, you would run:
```
python3 src/network_health.py --ping-host 192.168.1.1 --number-of-packets 10 --disable-datadog-submit
```

# DataDog Metric Information
This tool will submit metrics to DataDog with results for each test.

These metrics are defined as:
1. network_health.bandwidth_local.bandwidth_value
    - Metric Type: `Rate`
    - Metric Unit: `megabyte`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
2. network_health.bandwidth_remote.bandwidth_value
    - Metric Type: `Rate`
    - Metric Unit: `megabyte`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
3. network_health.bandwidth_local.interval_value
    - Metric Type: `Rate`
    - Metric Unit: `second`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
4. network_health.bandwidth_remote.interval_value
    - Metric Type: `Rate`
    - Metric Unit: `second`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
5. network_health.ping_local.average_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
6. network_health.ping_remote.average_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
7. network_health.ping_local.max_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
8. network_health.ping_remote.max_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
9. network_health.ping_local.min_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
10. network_health.ping_remote.min_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
11. network_health.ping_local.standard_deviation_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
12. network_health.ping_remote.standard_deviation_latency
    - Metric Type: `Rate`
    - Metric Unit: `millisecond`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
13. network_health.ping_local.packet_loss
    - Metric Type: `Count`
    - Metric Unit: `percent`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 
14. network_health.ping_remote.packet_loss
    - Metric Type: `Count`
    - Metric Unit: `percent`
    - Tag Key: `host`
    - Tag Value: `$HOSTNAME` 