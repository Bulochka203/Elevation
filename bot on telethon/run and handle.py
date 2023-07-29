from telethon import TelegramClient, events
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError, ChatAdminRequiredError
from utils import result_table, find_nickname, sub_text, get_link_table
from telethon.tl.types import ChannelParticipantsSearch, PeerUser
from credentials import token, api_id, api_hash, token_adara, token_x_force

import text
import logging
import kb

t_channels = ["X_lFORCE", "clan_moon_light"]
client = TelegramClient('x_force', api_id, api_hash)


async def check(t_channel, nickname):
    try:
        user_id = await client.get_entity(nickname)
        channel = await client(ResolveUsernameRequest(t_channel))
        async for _user in client.iter_participants(entity=channel, search=nickname):
            logging.debug(_user)
            if _user.id != user_id.id:
                return 2  # await re_check(t_channel, nickname)
            if _user.username.lower() == nickname.lower():
                return 1
    except UsernameNotOccupiedError:
        return 3
    except ValueError:
        return 3


async def re_check(t_channel, nickname):
    result = await client(GetParticipantsRequest(
        channel=t_channel,
        filter=ChannelParticipantsSearch(nickname),
        limit=200,
        offset=0,
        hash=0
    ))
    if result:
        for i in result.users:
            logging.debug(i)
            if i.username.lower() == nickname.lower():
                return False
    return True


@client.on(events.CallbackQuery(data=b'table_pattern'))
async def some_func(event):
    await event.respond("функция в доработке")


@client.on(events.CallbackQuery(data=b'table_link'))
async def check_admin_rights(event):
    await event.respond("функция в доработке")


@client.on(events.CallbackQuery(data=b'table_mesh'))
async def edit_mesh(event):
    await event.respond("функция в доработке")


@client.on(events.CallbackQuery(data=b'channel_pattern'))
async def change_config(event):
    await event.respond("функция в доработке")


@client.on(events.NewMessage(pattern='/start'))
async def hello(msg):
    if isinstance(msg.peer_id, PeerUser):
        entity = msg.peer_id
        await client.send_message(entity=entity, message=text.greet, buttons=kb.menu)


@client.on(events.NewMessage(pattern='Проверка'))
@client.on(events.NewMessage(pattern='📝 Проверить подписки'))
async def check_hello(msg):
    if isinstance(msg.peer_id, PeerUser):
        entity = msg.peer_id
        confs = ["@"+str(i) for i in t_channels]
        conf = "Текущий конфиг каналов: " + str(confs).removeprefix("[").removesuffix("]")
        await client.send_message(entity=entity, message=conf)
        await client.send_message(entity=entity, message=text.check_hello)


@client.on(events.NewMessage(pattern='Таблица'))
@client.on(events.NewMessage(pattern='🖼 Генерировать таблицу'))
async def check_ss(msg):
    if isinstance(msg.peer_id, PeerUser):
        entity = msg.peer_id
        await client.send_message(entity=entity, message="текущая таблица для подсчета: " + get_link_table())
        await client.send_message(entity=entity, message=text.results_hello)


@client.on(events.NewMessage(pattern='🔎Помощь'))
@client.on(events.NewMessage(pattern='Помощь'))
@client.on(events.NewMessage(pattern='/help'))
async def helper(msg):
    if isinstance(msg.peer_id, PeerUser):
        entity = msg.peer_id
        await client.send_message(entity=entity, message=text.helper, buttons=kb.help_buttons)


@client.on(events.NewMessage(pattern='Настройки'))
@client.on(events.NewMessage(pattern='🛠Настройки'))
@client.on(events.NewMessage(pattern='/settings'))
async def my_settings(msg):
    if isinstance(msg.peer_id, PeerUser):
        entity = msg.peer_id
        await client.send_message(entity=entity, message=text.settings, buttons=kb.settings)


@client.on(events.NewMessage(pattern='Отзывы'))
@client.on(events.NewMessage(pattern='🧾Отзывы'))
@client.on(events.NewMessage(pattern='/reviews'))
async def reviews(msg):
    if isinstance(msg.peer_id, PeerUser):
        entity = msg.peer_id
        await client.send_message(entity=entity, message=text.review, buttons=kb.review)


@client.on(events.NewMessage(pattern='Профиль'))
@client.on(events.NewMessage(pattern='👤Профиль'))
@client.on(events.NewMessage(pattern='/profile'))
async def profile(msg):
    if isinstance(msg.peer_id, PeerUser):
        entity = msg.peer_id
        some_ent = await msg.get_sender()
        await client.send_message(entity=entity,
                                  message="📋Имя пользователя: " + some_ent.first_name +
                                          "\n\n ⚙️ID Пользователя: " + str(some_ent.id) +
                                          "\n\n 📟 Никнейм пользователя: @" + some_ent.username
                                  )


@client.on(events.NewMessage(pattern='/check'))
async def checky(msg):
    entity = msg.peer_id
    prompt = await find_nickname(msg.text)
    logging.info(prompt)

    if not prompt:
        await client.send_message(entity=entity, message=text.check_nope)
        return

    counter = 0
    await client.send_message(entity=entity, message=text.wait)
    try:
        for channel in t_channels:
            for nickname in prompt:
                sub = await check(channel, nickname)
                if sub == 0 or sub is None:
                    logging.info(await sub_text(nickname, channel, "ns"))
                    await client.send_message(entity=entity, message=await sub_text(nickname, channel, "ns"))
                if sub == 1:
                    logging.info(await sub_text(nickname, channel, "os"))
                    counter += 1
                if sub == 2:
                    value = await re_check(channel, nickname)
                    if value:
                        logging.info(await sub_text(nickname, channel, "ns"))
                        await client.send_message(entity=entity, message=await sub_text(nickname, channel, "ns"))
                    else:
                        logging.info(await sub_text(nickname, channel, "os"))
                        counter += 1
                    # logging.info(await sub_text(nickname, channel, "es"))
                    # await client.send_message(entity=entity, message=await sub_text(nickname, channel, "es"))
                if sub == 3:
                    await client.send_message(entity=entity, message=await sub_text(nickname, channel, "ex"))
                    await client.send_message(entity=entity, message="Подписка на все каналы❌")
                    return
        if counter == len(prompt) * len(t_channels):
            await client.send_message(entity=entity, message="Подписка на все каналы✅")
        else:
            await client.send_message(entity=entity, message="Подписка на все каналы❌")
    except ChatAdminRequiredError:
        await client.send_message(entity=entity, message="Нет админки на одном из каналов")


@client.on(events.NewMessage(pattern='/results'))
async def generate_table(msg):
    entity = msg.peer_id
    print(msg.text)
    res = ''.join(filter(lambda i: i.isdigit(), msg.text))
    print(res)
    if res:
        await result_table(res)
    else:
        await result_table('1')
    await client.send_file(entity=entity, file='test.png')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client.start(bot_token=token_x_force)
    client.run_until_disconnected()
