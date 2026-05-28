import json
import subprocess
import sys
from unittest.mock import MagicMock, patch

# Mock httpx before importing app.discover
mock_httpx = MagicMock()
sys.modules["httpx"] = mock_httpx

import ipaddress
from app.discover import _local_ipv4_networks

def test_local_ipv4_networks_success():
    mock_output = [
        {
            "ifname": "eth0",
            "addr_info": [
                {
                    "family": "inet",
                    "local": "192.168.1.5",
                    "prefixlen": 24
                }
            ]
        },
        {
            "ifname": "eth1",
            "addr_info": [
                {
                    "family": "inet",
                    "local": "10.0.0.5",
                    "prefixlen": 8
                }
            ]
        }
    ]
    with patch("subprocess.check_output") as mock_run:
        mock_run.return_value = json.dumps(mock_output)
        nets = _local_ipv4_networks()

        assert len(nets) == 2
        assert ipaddress.IPv4Network("192.168.1.0/24") in nets
        assert ipaddress.IPv4Network("10.0.0.0/8") in nets

def test_local_ipv4_networks_filtering():
    mock_output = [
        {
            "ifname": "lo",
            "addr_info": [
                {
                    "family": "inet",
                    "local": "127.0.0.1",
                    "prefixlen": 8
                }
            ]
        },
        {
            "ifname": "eth0",
            "addr_info": [
                {
                    "family": "inet6",
                    "local": "fe80::1",
                    "prefixlen": 64
                },
                {
                    "family": "inet",
                    "local": "169.254.1.1",
                    "prefixlen": 16
                },
                {
                    "family": "inet",
                    "local": "192.168.1.5",
                    "prefixlen": 32
                },
                {
                    "family": "inet",
                    "local": "192.168.1.10",
                    "prefixlen": 24
                }
            ]
        }
    ]
    with patch("subprocess.check_output") as mock_run:
        mock_run.return_value = json.dumps(mock_output)
        nets = _local_ipv4_networks()

        # Should only have 192.168.1.0/24
        assert len(nets) == 1
        assert ipaddress.IPv4Network("192.168.1.0/24") in nets

def test_local_ipv4_networks_deduplication():
    mock_output = [
        {
            "ifname": "eth0",
            "addr_info": [
                {
                    "family": "inet",
                    "local": "192.168.1.5",
                    "prefixlen": 24
                }
            ]
        },
        {
            "ifname": "eth0:1",
            "addr_info": [
                {
                    "family": "inet",
                    "local": "192.168.1.6",
                    "prefixlen": 24
                }
            ]
        }
    ]
    with patch("subprocess.check_output") as mock_run:
        mock_run.return_value = json.dumps(mock_output)
        nets = _local_ipv4_networks()

        assert len(nets) == 1
        assert ipaddress.IPv4Network("192.168.1.0/24") in nets

def test_local_ipv4_networks_error_handling():
    # Subprocess error
    with patch("subprocess.check_output") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "ip")
        nets = _local_ipv4_networks()
        assert nets == []

    # Malformed JSON
    with patch("subprocess.check_output") as mock_run:
        mock_run.return_value = "not a json"
        nets = _local_ipv4_networks()
        assert nets == []
