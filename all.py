import re
from telethon.sync import TelegramClient
import hashlib

# Use your own values from my.telegram.org
api_id = 25315069
api_hash = '419b7cd9f055a855ffd2f06948ab882e'
#api_id = 14730333
#api_hash = '07be164bbc0521510c9c86d258b9da8e'

# The first parameter is the .session file name (absolute paths allowed)
#with TelegramClient('anon', api_id, api_hash) as client:
#    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))
message_hashes = ['b12f0faf0297b88cfc934d7bfac21f12','f8534821f227bfbd684298541b8aed89','aca7d20c3e45d0cd629b116c32d7062d']

with TelegramClient('anon', api_id, api_hash) as client:

    msg_cache = ""
    sender = ""
    date = ""
    for message in client.iter_messages(1001417778781,reverse=True):
        user= "Anonymous"
        if (hasattr(message.sender, 'username')):
          user=message.sender.username
        print(message.date, ' ', user, ' ', message.message)

#      if message.sender.username == sender:
#        
#        msg_cache += message.message
#
#      else:
#
#        if msg_cache:
#
#          # print cached message
#          print(date, ' ', sender, ' ', msg_cache += message.message)
#          msg_cache = ""
#
#          # cache new message
#          sender = message.sender.username
#          date = message.date
#          msg_cache = message.message
#
#        else: 
#
#          # cache new message
#          sender = message.sender.username
#          date = message.date
#          msg_cache = message.message

#          print(message.date, ' ', message.sender.username, ' ', message.message)

#@client.on(events.NewMessage(chats=[5427745665,1001417778781,1001778520278],pattern=r'.*\d?\d:\d\d-\d?\d:\d\d'))
#@client.on(events.NewMessage(chats=[1001417778781],pattern=r'.*\d?\d:\d\d-\d?\d:\d\d'))
#        print( event.stringify)
#  if 474122935 == event.user_id:           # Alexander
#  if 358409707 == sender_id or 474122935 == sender_id:           # Valery
#    if 'hello' in event.raw_text or 'good' in event.raw_text:
#        await event.reply('hi!')
#        print(event)
#        await event.forward_to(5427745665)
#        await message.forward_to(5569117599) # bot
#        await event.forward_to('me', silent=False)
#        await event.pin(54616533)
#

