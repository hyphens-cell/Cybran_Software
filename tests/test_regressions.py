"""Сбои, воспроизведённые независимым финальным аудитом."""
import pytest


@pytest.mark.parametrize('bad_text', ['bad\x01text', 'bad\x0btext', 'bad\ud800text', 'bad\ufffetext'])
def test_illegal_xml_and_unicode_input_cannot_poison_reports(api, rows, login, client, bad_text):
    response = api('POST', '/api/transactions/add', data={
        'fund_id':1,'type':'income','money':100,'pay_type':'Kaspi','description':bad_text})
    assert response.status_code == 400
    assert rows('SELECT id FROM Transactions') == []
    login('investor')
    assert client.get('/reports/export?format=xlsx').status_code == 200


def test_non_ascii_csrf_is_rejected_without_server_error(client, login):
    login('admin')
    assert client.post('/logout', data={'csrf_token':'я'}).status_code == 400
    assert client.get('/funds').status_code == 200


def test_security_headers_include_csp_and_permissions_policy(client):
    response = client.get('/login')
    assert response.headers['Content-Security-Policy'].startswith("default-src 'self'")
    assert "object-src 'none'" in response.headers['Content-Security-Policy']
    assert response.headers['Permissions-Policy'] == 'camera=(), geolocation=(), microphone=()'


@pytest.mark.parametrize('value',['0001-01-01T00:00:00+01:00','9999-12-31T23:59:59-01:00'])
def test_timezone_overflow_is_validation_error(api, rows, value):
    response = api('POST','/api/transactions/add',data={
        'fund_id':1,'type':'income','money':100,'pay_type':'Kaspi','datetime':value})
    assert response.status_code == 400
    assert rows('SELECT id FROM Transactions') == []


def test_excessively_long_identifier_is_validation_error(api):
    assert api('GET','/api/transactions',query_string={'fund_id':'1'*5000}).status_code == 400


def test_malformed_unicode_password_is_validation_error(api, rows):
    response = api('POST','/api/create_user','root',{
        'username':'malformed','fullname':'Test','role':'Admin','password':'password\ud800'})
    assert response.status_code == 400
    assert rows("SELECT id FROM Users WHERE username='malformed'") == []


@pytest.mark.parametrize('value', [
    '0.009999999999999999999999999999999',
    '1.230000000000000000000000000001',
    '0.0000000000000000000000000000001',
])
def test_html_subcent_values_are_never_silently_rounded(login, html_post, rows, value):
    login('cashier')
    response = html_post('/cashier',{'amount':value,'fund_id':'1','pay_type':'Kaspi'})
    assert response.status_code == 400
    assert rows('SELECT id FROM Transactions') == []


@pytest.mark.parametrize('value,expected', [('1.230000000000000000000000000000',123),
                                         ('92233720368547758.07',9223372036854775807)])
def test_html_exact_values_preserve_all_minor_units(login, html_post, rows, value, expected):
    login('cashier')
    assert html_post('/cashier',{'amount':value,'fund_id':'1','pay_type':'Kaspi'}).status_code == 302
    assert rows('SELECT money FROM Transactions') == [{'money':expected}]
