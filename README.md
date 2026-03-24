# Zhuki Bot (aiogram edition)

Telegram-бот на **aiogram 3** для игровых «атак жуками»: пользователи подписываются, кидают друг в друга жуков, объединяются в сквады и участвуют в рейтинге.

## Что изменено

- Полный переход на `aiogram` для runtime-бота и скрипта рассылки.
- Переписан `main.py` на Router/Dispatcher архитектуру aiogram 3.
- Оставлено надежное сохранение данных из предыдущего рефакторинга (атомарная запись JSON).
- Сохранены и обновлены команды для базового геймплея: подписка, броски, сквады, рейтинг.

## Команды

- `/start`
- `/subscribe`
- `/unsubscribe`
- `/bug_count`
- `/leaderboard`
- `/throw @username`
- `/create_squad [name]`
- `/join_squad <squad_id>`
- `/my_squad`

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Установите env-переменные:

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

Рассылка:

```bash
python broadcast_message.py
```

Тесты:

```bash
python -m unittest discover -s tests
```
