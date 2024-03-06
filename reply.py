#!/usr/bin/python3

from telethon import TelegramClient, events

# Use your own values from my.telegram.org
api_id = 14730333
api_hash = '07be164bbc0521510c9c86d258b9da8e'

# The first parameter is the .session file name (absolute paths allowed)
#with TelegramClient('anon', api_id, api_hash) as client:
#    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))

client = TelegramClient('anon', api_id, api_hash)

#@client.on(events.NewMessage(chats=[5427745665,1001417778781,1001778520278],pattern=r'.*\d?\d:\d\d-\d?\d:\d\d'))
@client.on(events.NewMessage(chats=[1001417778781],pattern=r'.*\d?\d:\d\d-\d?\d:\d\d\ \d'))
async def my_event_handler(event):
#        print( event.stringify)
#  if 474122935 == event.user_id:           # Alexander
  if 358409707 == event.peer_id.user_id or 474122935 == event.peer_id.user_id:           # Valery
#    if 'hello' in event.raw_text or 'good' in event.raw_text:
#        await event.reply('hi!')
        print(event)
#        await event.forward_to(5427745665)
        await event.forward_to(5569117599) # bot
#        await event.forward_to('me', silent=False)
#        await event.pin(54616533)

#
#@client.on(events.UserUpdate)
#async def handler(event):
#    # If someone is uploading, say something
##  if 5427745665 == event.user_id:           # Agentsky
##    if event.uploading:
##    if event.online:
#    sender = await client.get_entity(event.user_id)
#
#    print( 'U:', event.user_id, ' s:', sender.username, sender.phone, event)
#    if event.typing:
#        print( event.user_id)
##        await client.send_message(event.user_id, 'What are you sending?')
#        await client.send_message('me', "test", silent=False)
#
client.start()
client.run_until_disconnected()
