# ping_exporter

Spin a web server to export ping metrics. Can use several targets to ping and include most of the data returned by the ICMP module in Python. You can then collect them with Prometheus.

## Requirements

- Python3
- Ability to send ICMP packets for the user running ping_exporter

## Installation


### Ansible

Check [ansible-role-ping_exporter](https://github.com/ajdelgado/ansible-role-ping_exporter).

### Linux
Tested in Ubuntu 20.10

1. Check that you can send ICMP packets. You can set extend the group range able to do it with:
```bash
echo 'net.ipv4.ping_group_range = 0 2147483647' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```
2. Install the script system-wide with:
```bash
sudo python3 setup.py install
```

## Usage

Usage: ping_exporter.py [OPTIONS]
```
Options:
  -d, --debug-level [CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
                                  Set the debug level for the standard output.
  -l, --log-file TEXT             File to store all debug messages.
  -t, --targets TEXT              IP address of the target to ping.
  -c, --count INTEGER             Number of packets to send.
  -p, --port INTEGER RANGE        Port to listen for collector to fetch
                                  metrics.  [1<=x<=65535]
  -f, --frequency FLOAT RANGE     Time between gathering pings.
                                  [0.01<=x<=99999]
  -i, --interval FLOAT RANGE      Time between packets sent.  [0.01<=x<=99999]
  -o, --timeout FLOAT RANGE       The maximum waiting time for receiving a
                                  reply in seconds.  [0.01<=x<=99999]
  -a, --family [4|6]              IP family version to use.
  --config FILE                   Read configuration from FILE.
  --help                          Show this message and exit.
```