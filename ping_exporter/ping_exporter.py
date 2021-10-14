#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This script is licensed under GNU GPL version 2.0 or above
# (c) 2021 Antonio J. Delgado
# 

import sys
import os
import logging
import click
import click_config_file
from logging.handlers import SysLogHandler
from prometheus_client import start_http_server, Gauge
from icmplib import multiping
import ipaddress
import time

class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class ping_exporter:

    def __init__(self, debug_level, log_file, targets, count, port, frequency, interval, timeout, family):
        ''' Initial function called when object is created '''
        self.debug_level = debug_level
        if log_file is None:
            log_file = os.path.join(os.environ.get('HOME', os.environ.get('USERPROFILE', os.getcwd())), 'log', 'ping_exporter.log')
        self.log_file = log_file
        self._init_log()
        self.targets = targets
        self.count = count
        self.port = port
        self.frequency = frequency
        self.interval = interval
        self.timeout = timeout
        self.family = int(family)
        self.icmp_avg_gauge = Gauge('ping_average_round_trip', 'Average time of round-trip ping to target', ['target'])
        self.icmp_lost_packets = Gauge('ping_lost_packets', 'Percent of packets lost pinging target (0 to 1)', ['target'])
        self.icmp_jitter = Gauge('ping_jitter', 'The jitter in milliseconds, defined as the variance of the latency of packets flowing through the network (0 to 1)', ['target'])
        self.icmp_gauge = dict()
        for index in range(0, self.count):
            self.icmp_gauge[index] = Gauge(f"ping_round_trip_{index}", f"Time of round-trip count {index} ping to target", ['target'])
        self._log.info(f"Listening in http://localhost:{self.port}/metrics")
        start_http_server(self.port)
        while True:
            self._log.debug('Gathering metrics')
            self.gather_metrics()
            self._log.debug(f"Waiting {self.frequency} seconds")
            time.sleep(self.frequency)


    def _init_log(self):
        ''' Initialize log object '''
        self._log = logging.getLogger("ping_exporter")
        self._log.setLevel(logging.DEBUG)

        sysloghandler = SysLogHandler()
        sysloghandler.setLevel(logging.DEBUG)
        self._log.addHandler(sysloghandler)

        streamhandler = logging.StreamHandler(sys.stdout)
        streamhandler.setLevel(logging.getLevelName(self.debug_level))
        #formatter = '%(asctime)s | %(levelname)8s | %(message)s'
        formatter = '[%(levelname)s] %(message)s'
        streamhandler.setFormatter(CustomFormatter(formatter))
        self._log.addHandler(streamhandler)

        if not os.path.exists(os.path.dirname(self.log_file)):
            os.mkdir(os.path.dirname(self.log_file))

        filehandler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=102400000)
        # create formatter
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.DEBUG)
        self._log.addHandler(filehandler)
        return True

    def ping(self):
        try:
            hosts = multiping(self.targets, family=self.family, interval=self.interval, timeout=self.timeout, count=self.count, privileged=False)
            return hosts
        except:
            self._log.error('Check that you can send ICMP packets. You can set extend the group range able to do it with: echo \'net.ipv4.ping_group_range = 0 2147483647\' | sudo tee -a /etc/sysctl.conf; sudo sysctl -p')
            return False

    def gather_metrics(self):
        self._log.debug(f"Pinging targets '{', '.join(self.targets)}'")
        self.hosts = self.ping()
        for host in self.hosts:
            self._log.debug(f"Results for host: {host.address}")
            self._log.debug(f"  Average round trip: {host.avg_rtt}")
            self.icmp_avg_gauge.labels(host.address).set(host.avg_rtt)
            self._log.debug(f"  Percent packets lost: {host.packet_loss}")
            self.icmp_lost_packets.labels(host.address).set(host.packet_loss)
            self._log.debug(f"  Jitter: {host.jitter}")
            self.icmp_jitter.labels(host.address).set(host.jitter)
            for index in range(0, len(host.rtts)):
                self._log.debug(f"  Time rtt {index}: {host.rtts[index]}")
                self.icmp_gauge[index].labels(host.address).set(host.rtts[index])

def validate_ip(ctx, param, value):
    ''' Check if a parameter is a valid IP address '''
    for item in value:
        try:
            anip = ipaddress.ip_address(item)
        except:
            raise click.BadParameter(f"{item} is not a valid IP address.")
    return value

@click.command()
@click.option("--debug-level", "-d", default="INFO",
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
        case_sensitive=False,
    ), help='Set the debug level for the standard output.')
@click.option('--log-file', '-l', help="File to store all debug messages.")
@click.option('--targets', '-t', default=["1.1.1.1"], multiple=True, callback=validate_ip, help="IP address of the target to ping.")
@click.option('--count', '-c', default=4, type=int, help="Number of packets to send.")
@click.option('--port', '-p', default=8787, type=click.IntRange(1, 65535), help="Port to listen for collector to fetch metrics.")
@click.option('--frequency', '-f', default=10, type=click.FloatRange(0.01, 99999), help="Delay between pings to each host.")
@click.option('--interval', '-i', default=1, type=click.FloatRange(0.01, 99999), help="Time between packets sent.")
@click.option('--timeout', '-o', default=2, type=click.FloatRange(0.01, 99999), help="The maximum waiting time for receiving a reply in seconds.")
@click.option('--family', '-a', default="4", type=click.Choice(["4", "6"]), help="IP family version to use.")
@click_config_file.configuration_option()
def __main__(debug_level, log_file, targets, count, port, frequency, interval, timeout, family):
    object = ping_exporter(debug_level, log_file, targets, count, port, frequency, interval, timeout, family)

if __name__ == "__main__":
    __main__()

