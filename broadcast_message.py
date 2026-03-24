# --- imports ---

from __future__ import annotations

import asyncio

import config
import pyrogram


# --- execution ---

async def broadcast_message(app: pyrogram.Client, message_text: str, photo_url: str | None = None) -> int:
    user_ids = list(config.load().users.keys())
    if not user_ids:
        print('Нет пользователей для рассылки.')
        return 0

    delivered = 0
    for user_id in user_ids:
        try:
            if photo_url:
                await app.send_photo(user_id, photo=photo_url, caption=message_text)
            else:
                await app.send_message(user_id, message_text)
            delivered += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f'Ошибка отправки пользователю {user_id}:\n{e}')

    return delivered


# --- start ---

if __name__ == '__main__':
    app = pyrogram.Client(
        'broadcast_test' if config.TEST else 'broadcast',
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN_TEST if config.TEST else config.BOT_TOKEN_MAIN,
    )

    async def _runner() -> None:
        await app.start()
        try:
            delivered = await broadcast_message(app, input('>> '))
            print(f'Отправлено сообщений: {delivered}')
        finally:
            await app.stop()

    asyncio.run(_runner())
