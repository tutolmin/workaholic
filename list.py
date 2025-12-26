from telethon import TelegramClient

# Use your own values from my.telegram.org
#api_id = 14730333
#api_hash = '07be164bbc0521510c9c86d258b9da8e'
api_id = 25315069
api_hash = '419b7cd9f055a855ffd2f06948ab882e'

# The first parameter is the .session file name (absolute paths allowed)
#with TelegramClient('anon', api_id, api_hash) as client:
#    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))

client = TelegramClient('anon', api_id, api_hash)

async def main():
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)

    # ...to your contacts
#    await client.send_message(5427745665, 'Hello, friend!')
#    await client.send_message(1001546209198, 'Hello, friends!')



with client:
    client.loop.run_until_complete(main())

