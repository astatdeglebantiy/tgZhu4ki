# Zhuki WhatsApp Bot

Telegram-бот для игровых «атак жуками»: пользователи подписываются, кидают друг в друга жуков, объединяются в сквады и участвуют в ивентах.

## Что улучшено

- Более надежное сохранение данных (атомарная запись JSON).
- Поддержка переменных окружения для ключей и режима TEST/PROD.
- Исправлены импорты ивентов.
- Улучшен CLI-скрипт рассылки (корректный `start/stop`, отчет по доставке).
- Добавлены базовые автоматические тесты сериализации и сохранения.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Создайте переменные окружения:

```bash
export API_ID=123456
export API_HASH="your_api_hash"
export BOT_TOKEN_MAIN="123:main_token"
export BOT_TOKEN_TEST="123:test_token"
export TEST=true
```

Запуск бота:

```bash
python main.py
```

Запуск тестов:

```bash
python -m unittest discover -s tests
```

## Структура проекта

- `main.py` — основной Telegram bot runtime.
- `classes.py` — доменные классы и модели статуса.
- `events.py` — сценарии ивентов.
- `config.py` — загрузка/сохранение данных и конфиг из env.
- `broadcast_message.py` — рассылка всем пользователям.
- `tests/` — smoke/unit тесты сериализации.
