# Бот CryptoParser
<hr>
Бот, обрабатывающий отчёты с площадки Binance.

## Запуск бота

Чтобы запустить бота на сервере необходимо:

1. Создать файл `.env` и указать там следующие параметры:
   1. **TELEGRAM_TOKEN** – api-token бота телеграмм.
   2. **ADMINS** - Список ID пользователей-админов через запятую.
2. Создать файл `database.ini` и заполнить в нём поля:
   1. host – Имя хоста (по умолчанию `localhost`);
   2. dbname – Название БД (по умолчанию `acces_codes`);
   3. user – Имя пользователя (по умолчанию `postgresql`);
   4. password – Пароль (по умолчанию `123qweasd`);
3. Скачать `postgresql`.
4. Скачать `redis`.

Установка автозапуска:
1) Отключить бота
2) sudo nano /etc/systemd/system/<name_bot>.service
3) В файл поместить код:
[Unit]
Description=<namebot> - Telegram bot
After=network.target

[Service]
User=deepak
Group=admin
Type=simple
Restart=always
ExecStart=/usr/bin/python3 <Путь до директории бота>/run.py
 
[Install]
WantedBy=multi-user.target


4) sudo systemctl daemon-reload
5) sudo systemctl enable test.service 
6) sudo systemctl start test.service - бот должен заработать


Команды:
7) sudo systemctl stop name_of_your_service - Остановка
8) sudo systemctl restart name_of_your_service - Перезагрузка
9) sudo systemctl status name_of_your_service - Проверка статуса
