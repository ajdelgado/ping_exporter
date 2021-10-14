# ping_exporter

Spin a web server to export ping metrics. Can use several targets to ping and include most of the data returned by the ICMP module in Python. You can then collect them with Prometheus.

## Requirements

- Python3
- Ability to send ICMP packets for the user running ping_exporter

## Installation

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

  ```bash
  ping_exporter.py [--debug-level|-d CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET] # Other parameters
  ```
