# --- imports ---

import random
from datetime import timedelta

from classes import BasicEvent, Status


# --- events ---

invasion_of_bugs = BasicEvent(
    name='invasion_of_bugs',
    new_status=Status(rate_limit=3, window_duration=timedelta(minutes=15)),
    duration=1 * 60 * 60,
    start_message='🚨🚨🚨🚨🚨\n\n\n🔮🧿🧿🧿🔮 БЕШАСТЬ 🔮🪬🪬🪬🔮\n\n🪲🪲БЕШАСТИ: Нашествие жуков⚠️⚠️ НАЧАЛИСЬ!🔮🔮\n📢 СРОЧНО ОБРАБОТАЙТЕ🤙 ВАШЕ УСТРОЙСТВО📱 ДИХЛОФОЗОМ🧴\nВ течение 1 часа каждому пользователю разрешается отправлять до 3 жуков каждые 15 минут.\n\n\n🚨🚨🚨🚨🚨',
    start_message_photo='https://imgur.com/k2O1o1B',
    end_message='🚨🚨🚨🚨🚨\n\n\nПУСТОЙ БОБОФОН🫘🫘👽 УЖЕ ЗА ДВЕРЬЮ👹👹\n\nБЕШАСТИ: Нашествие жуков⚠️⚠️ завершены. Таймауты возвращены в обычный режим.\n\n\n🚨🚨🚨🚨🚨',
)

gas_attack = BasicEvent(
    name='gas_attack',
    new_status=Status(
        rate_limit=2,
        window_duration=timedelta(minutes=15),
        count=-1,
        send_message=lambda _from, to, count, bug_declination: random.choice([
            f'@{_from} отдихлофосил @{to} (всего ×{count} {bug_declination(count)})',
        ]),
        end_window_error_message=lambda hours, minutes, seconds:
        f'БЕШАСТИ🔮🔮\n⚠️⚠️ У Вас кончился ГАЗ❗️❗️\n\nВы сможете отдихлофосить🦨💨 снова через {hours} ч. {minutes} мин. {seconds} сек. 🧴🧴',
        error_message=lambda: 'БЕШАСТИ ❗️❗️❗️ Не удалось отдихлофостить🦨💨. Попробуйте снова.',
    ),
    duration=2 * 60 * 60,
    start_message='🚨🚨🚨🚨🚨\n\n\n🔮🧿🧿🧿🔮 БЕШАСТЬ 🔮🪬🪬🪬🔮\n\n🦨💨БЕШАСТИ: Газовая атака🧴⚠️ НАЧАЛИСЬ!🔮🔮\n📢 СРОЧНО СОХРАНИТЕ🤙 ВАШИХ ЖУКОВ🪲🪲 В БАНКУ🫙\nВ течение 2 часов каждому пользователю разрешается отправлять до 2 газовых атак каждые 15 минут другому пользователю при условии что у другого пользователя Жуков🪲🪲 больше чем 0.\n\n\n🚨🚨🚨🚨🚨',
    start_message_photo='https://imgur.com/a/eJ92fKs',
    end_message='🚨🚨🚨🚨🚨\n\n\nПОЛНЫЙ БОБОФОН🫘🫘👽 УЖЕ ЗА ДВЕРЬЮ👹👹\n\n🦨💨БЕШАСТИ: Газовая атака🧴⚠️ завершены. Таймауты и кидалово жуков возвращены в обычный режим.\n\n\n🚨🚨🚨🚨🚨',
)
