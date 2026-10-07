import pytest

from app import mobile


def test_mobile_urls_validate_port_and_private_addresses(monkeypatch):
    monkeypatch.setattr(mobile, 'discover_lan_ipv4', lambda: ['192.168.6.139', '192.168.137.1'])
    assert mobile.mobile_urls(5000) == [
        'http://192.168.6.139:5000', 'http://192.168.137.1:5000'
    ]
    with pytest.raises(ValueError):
        mobile.mobile_urls(70000)


def test_address_filter_rejects_public_loopback_and_duplicates():
    assert mobile._usable_ipv4(['127.0.0.1', '8.8.8.8', '169.254.1.2',
                                '192.168.6.139', '192.168.6.139', 'invalid']) == ['192.168.6.139']


def test_terminal_qr_contains_real_modules():
    qr = mobile.render_terminal_qr('http://192.168.6.139:5000')
    assert len(qr.splitlines()) >= 10
    assert '█' in qr
    assert any(character in qr for character in ('▀', '▄'))
