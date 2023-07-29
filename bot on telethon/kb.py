from telethon.tl.types import (
    ReplyInlineMarkup,
    ReplyKeyboardMarkup,
    KeyboardButtonRow,
    KeyboardButton,
    KeyboardButtonUrl,
    KeyboardButtonCallback,
)


help_buttons = ReplyInlineMarkup([
    KeyboardButtonRow([
        KeyboardButtonUrl(text="Туториал по проверке подписок", url="https://youtu.be/Q8KDUzbt3Vs"),

    ]),
    KeyboardButtonRow([
        KeyboardButtonUrl(text="Туториал по генерации таблиц результатов", url="https://t.me/ups_bulochka203"),
    ])
])

review = ReplyInlineMarkup([
    KeyboardButtonRow([
        KeyboardButtonUrl(text="Отзывы об использовании бота", url="https://t.me/rewiew_elevation"),
    ]),
])

settings = ReplyInlineMarkup([
    KeyboardButtonRow([
        KeyboardButtonCallback(text="Изменить шаблон таблицы", data=b'table_pattern'),
    ]),
    KeyboardButtonRow([
        KeyboardButtonCallback(text="Изменить ссылку на гугл таблицу", data=b'table_link'),
    ]),
    KeyboardButtonRow([
        KeyboardButtonCallback(text="Изменить каналы проверки подписок", data=b'channel_pattern'),
    ]),
    KeyboardButtonRow([
        KeyboardButtonCallback(text="Настроить сетку таблицы вручную", data=b'table_mesh'),
    ]),
])

menu = ReplyKeyboardMarkup([
    KeyboardButtonRow([
        KeyboardButton(text='🖼 Генерировать таблицу'),
        KeyboardButton(text='📝 Проверить подписки')
    ]),
    # KeyboardButtonRow([
    #   KeyboardButton(text='Баланс'),
    #   KeyboardButton(text='Разработчик'),
    #   KeyboardButton(text='Расценки'),
    # ]),
    KeyboardButtonRow([
        KeyboardButton(text='🔎Помощь'),
        KeyboardButton(text='👤Профиль'),
        KeyboardButton(text='🧾Отзывы'),
    ]),
    KeyboardButtonRow([
        KeyboardButton(text='🛠Настройки')
    ])
])
