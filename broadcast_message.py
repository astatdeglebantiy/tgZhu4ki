# --- imports ---

import asyncio
import config
import pyrogram


# --- execution ---

async def broadcast_message(app: pyrogram.Client, message_text: str, photo_url: str = None):
    user_ids = config.load().users.keys()
    if not user_ids:
        print("Нет пользователей для рассылки.")
        await app.stop()
        return
    for user_id in user_ids:
        try:
            if photo_url:
                await app.send_photo(user_id, photo=photo_url, caption=message_text)
            else:
                await app.send_message(user_id, message_text)

            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Ошибка отправки пользователю {user_id}:\n{e}")


# --- start ---

if __name__ == '__main__':
    app = pyrogram.Client("broadcast_test" if config.TEST else "broadcast", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN_TEST if config.TEST else config.BOT_TOKEN_MAIN)
    asyncio.run(broadcast_message(
        app,
        input('>>'))
    )
    app.stop()
