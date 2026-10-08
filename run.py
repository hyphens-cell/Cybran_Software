"""Точка запуска Waitress с LAN-адресом для телефона и QR-кодом в терминале."""
import os

from waitress import serve
from app import create_app
from app.mobile import mobile_urls, render_terminal_qr

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))
    # Сравниваем настроенный host; намеренная привязка к LAN указана выше.
    urls = mobile_urls(port) if host in ('0.0.0.0', '::') else [f'http://{host}:{port}']  # nosec B104
    print('\nCybran Software готов к подключению с телефона.')
    print(f'SQLite база: {app.config["DATABASE"]}')
    if app.config.get('DEMO_MODE'):
        print('\nВНИМАНИЕ: запущена демонстрационная база с тестовыми паролями. Используйте только в доверенной сети.')
    if host in ('0.0.0.0', '::') and not app.config['SESSION_COOKIE_SECURE']:  # nosec B104
        print('\nВНИМАНИЕ: LAN-подключение использует незашифрованный HTTP. Не используйте публичный или недоверенный Wi-Fi.')
    if urls:
        print(f'\nОткройте на телефоне: {urls[0]}\n')
        print(render_terminal_qr(urls[0]))
        if len(urls) > 1:
            print('\nДругие локальные адреса: ' + ', '.join(urls[1:]))
    else:
        print(f'\nЛокально: http://127.0.0.1:{port}')
        print('LAN-адрес не найден. Укажите MOBILE_IP перед запуском.')
    print('\nТелефон и компьютер должны быть в одной локальной сети. Для остановки нажмите Ctrl+C.\n', flush=True)
    serve(app, host=host, port=port)
