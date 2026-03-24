from __future__ import annotations

import asyncio

from aiogram import Bot

import config


async def broadcast_message(bot: Bot, message_text: str, photo_url: str | None = None) -> int:
    user_ids = list(config.load().users.keys())
    if not user_ids:
        print('Нет пользователей для рассылки.')
        return 0

    delivered = 0
    for user_id in user_ids:
        try:
            if photo_url:
                await bot.send_photo(user_id, photo=photo_url, caption=message_text)
            else:
                await bot.send_message(user_id, message_text)
            delivered += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f'Ошибка отправки пользователю {user_id}: {e}')

    return delivered


if __name__ == '__main__':
    token = config.BOT_TOKEN_TEST if config.TEST else config.BOT_TOKEN_MAIN

    async def _runner() -> None:
        bot = Bot(token)
        try:
            delivered = await broadcast_message(bot, input('>> '))
            print(f'Отправлено сообщений: {delivered}')
        finally:
            await bot.session.close()

    asyncio.run(_runner())
