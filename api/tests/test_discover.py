import pytest
import ipaddress
import asyncio
import json
from unittest.mock import patch, AsyncMock
from app.discover import discover, _parse_ip_addr_output

def test_discover_basic():
    # Mocking _local_ipv4_networks to return a small network
    # Mocking _tcp_connect to simulate open ports
    # Mocking _probe_hik_isapi to simulate Hikvision detection

    with patch("app.discover._local_ipv4_networks") as mock_nets, \
         patch("app.discover._tcp_connect", new_callable=AsyncMock) as mock_connect, \
         patch("app.discover._probe_hik_isapi", new_callable=AsyncMock) as mock_probe:

        # 192.168.1.0/29 has hosts .1 to .6
        mock_nets.return_value = [ipaddress.IPv4Network("192.168.1.0/29")]

        async def mock_connect_side_effect(ip, port, timeout):
            if ip == "192.168.1.1" and port == 80:
                return True
            if ip == "192.168.1.2" and port == 554:
                return True
            return False

        mock_connect.side_effect = mock_connect_side_effect

        async def mock_probe_side_effect(client, ip):
            if ip == "192.168.1.1":
                return True
            return False

        mock_probe.side_effect = mock_probe_side_effect

        results = asyncio.run(discover(timeout_sec=5))

        assert len(results) == 2
        # Sort order: Hikvision first, then by IP
        assert results[0].ip == "192.168.1.1"
        assert results[0].hikvision_isapi is True
        assert results[0].vendor_hint == "hikvision"

        assert results[1].ip == "192.168.1.2"
        assert results[1].onvif_hint is True
        assert results[1].hikvision_isapi is False

def test_local_ipv4_networks_parsing():
    mock_json_out = """
    [
        {
            "ifname": "eth0",
            "addr_info": [
                {
                    "family": "inet",
                    "local": "192.168.1.5",
                    "prefixlen": 24
                },
                {
                    "family": "inet6",
                    "local": "fe80::1",
                    "prefixlen": 64
                }
            ]
        },
        {
            "ifname": "lo",
            "addr_info": [
                {
                    "family": "inet",
                    "local": "127.0.0.1",
                    "prefixlen": 8
                }
            ]
        }
    ]
    """
    nets = _parse_ip_addr_output(json.loads(mock_json_out))
    assert len(nets) == 1
    assert str(nets[0]) == "192.168.1.0/24"
