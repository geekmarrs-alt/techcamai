import sys
import json
import asyncio
import subprocess
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# We need to import the module once to have access to its functions for testing
# but we must be careful not to pollute sys.modules if httpx is missing.
# Given the environment, we know it's missing, so we'll mock it during import.
with patch.dict("sys.modules", {"httpx": MagicMock()}):
    import api.app.discover as discover_mod
    from api.app.discover import (
        _local_ipv4_networks,
        _tcp_connect,
        _probe_hik_isapi,
        discover,
        DiscoveredDevice
    )

def test_imports():
    assert _local_ipv4_networks is not None
    assert _tcp_connect is not None
    assert _probe_hik_isapi is not None
    assert discover is not None

def test_local_ipv4_networks_happy_path():
    mock_out = [
        {
            "ifname": "eth0",
            "addr_info": [
                {"family": "inet", "local": "192.168.1.5", "prefixlen": 24}
            ]
        },
        {
            "ifname": "wlan0",
            "addr_info": [
                {"family": "inet", "local": "10.0.0.10", "prefixlen": 24}
            ]
        }
    ]
    with patch("subprocess.check_output", return_value=json.dumps(mock_out)):
        nets = _local_ipv4_networks()
        assert len(nets) == 2
        assert "192.168.1.0/24" in [n.with_prefixlen for n in nets]
        assert "10.0.0.0/24" in [n.with_prefixlen for n in nets]

def test_local_ipv4_networks_filtering():
    mock_out = [
        {
            "ifname": "lo",
            "addr_info": [
                {"family": "inet", "local": "127.0.0.1", "prefixlen": 8}
            ]
        },
        {
            "ifname": "eth0",
            "addr_info": [
                {"family": "inet6", "local": "fe80::1", "prefixlen": 64},
                {"family": "inet", "local": "169.254.1.1", "prefixlen": 16},
                {"family": "inet", "local": "192.168.1.5", "prefixlen": 32},
                {"family": "inet", "local": "192.168.1.5", "prefixlen": 24}
            ]
        }
    ]
    with patch("subprocess.check_output", return_value=json.dumps(mock_out)):
        nets = _local_ipv4_networks()
        assert len(nets) == 1
        assert nets[0].with_prefixlen == "192.168.1.0/24"

def test_local_ipv4_networks_dedupe():
    mock_out = [
        {
            "ifname": "eth0",
            "addr_info": [
                {"family": "inet", "local": "192.168.1.5", "prefixlen": 24}
            ]
        },
        {
            "ifname": "eth0:1",
            "addr_info": [
                {"family": "inet", "local": "192.168.1.6", "prefixlen": 24}
            ]
        }
    ]
    with patch("subprocess.check_output", return_value=json.dumps(mock_out)):
        nets = _local_ipv4_networks()
        assert len(nets) == 1
        assert nets[0].with_prefixlen == "192.168.1.0/24"

def test_local_ipv4_networks_error():
    with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "cmd")):
        nets = _local_ipv4_networks()
        assert nets == []

def test_tcp_connect_success():
    async def run():
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_writer.wait_closed = AsyncMock()

        with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
            result = await _tcp_connect("1.2.3.4", 80, 0.1)
            assert result is True
            mock_writer.close.assert_called_once()
    asyncio.run(run())

def test_tcp_connect_failure():
    async def run():
        with patch("asyncio.open_connection", side_effect=Exception("Connection refused")):
            result = await _tcp_connect("1.2.3.4", 80, 0.1)
            assert result is False
    asyncio.run(run())

def test_tcp_connect_timeout():
    async def run():
        async def slow_connect(*args, **kwargs):
            await asyncio.sleep(0.1)
            return MagicMock(), MagicMock()

        with patch("asyncio.open_connection", side_effect=slow_connect):
            result = await _tcp_connect("1.2.3.4", 80, 0.01)
            assert result is False
    asyncio.run(run())

def test_probe_hik_isapi_server_header():
    async def run():
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"server": "Hikvision-ISAPI/2.0"}
        mock_resp.text = ""
        mock_client.get.return_value = mock_resp

        result = await _probe_hik_isapi(mock_client, "1.2.3.4")
        assert result is True
    asyncio.run(run())

def test_probe_hik_isapi_text_hint():
    async def run():
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.headers = {}
        mock_resp.text = "Hikvision camera requires authentication"
        mock_client.get.return_value = mock_resp

        result = await _probe_hik_isapi(mock_client, "1.2.3.4")
        assert result is True
    asyncio.run(run())

def test_probe_hik_isapi_path_hint():
    async def run():
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.headers = {}
        mock_resp.text = "Forbidden"
        mock_client.get.return_value = mock_resp

        result = await _probe_hik_isapi(mock_client, "1.2.3.4")
        assert result is True
    asyncio.run(run())

def test_probe_hik_isapi_not_found():
    async def run():
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.headers = {}
        mock_resp.text = "Not Found"
        mock_client.get.return_value = mock_resp

        result = await _probe_hik_isapi(mock_client, "1.2.3.4")
        assert result is False
    asyncio.run(run())

def test_probe_hik_isapi_exception():
    async def run():
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Network error")

        result = await _probe_hik_isapi(mock_client, "1.2.3.4")
        assert result is False
    asyncio.run(run())

def test_discover_full():
    async def run():
        # Mock networks
        from ipaddress import IPv4Network
        mock_nets = [IPv4Network("192.168.1.0/30")] # .0 (net), .1, .2, .3 (broadcast)

        # Mock _tcp_connect to be open on 192.168.1.1:80 and 192.168.1.2:554
        async def mock_tcp(ip, port, timeout):
            if ip == "192.168.1.1" and port == 80: return True
            if ip == "192.168.1.2" and port == 554: return True
            return False

        # Mock _probe_hik_isapi
        async def mock_probe(client, ip):
            return ip == "192.168.1.1"

        with patch.object(discover_mod, "_local_ipv4_networks", return_value=mock_nets), \
             patch.object(discover_mod, "_tcp_connect", side_effect=mock_tcp), \
             patch.object(discover_mod, "_probe_hik_isapi", side_effect=mock_probe):

            results = await discover(timeout_sec=5)

            assert len(results) == 2
            # 192.168.1.1 should be first because it's hikvision
            assert results[0].ip == "192.168.1.1"
            assert results[0].vendor_hint == "hikvision"
            assert results[0].hikvision_isapi is True
            assert 80 in results[0].ports

            assert results[1].ip == "192.168.1.2"
            assert results[1].onvif_hint is True
            assert 554 in results[1].ports

    asyncio.run(run())

def test_discover_no_networks():
    async def run():
        with patch.object(discover_mod, "_local_ipv4_networks", return_value=[]):
            results = await discover()
            assert results == []
    asyncio.run(run())
