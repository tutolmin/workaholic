#!/usr/bin/python3 -u

from telethon import TelegramClient, events
import re
import random
import hashlib

# Use your own values from my.telegram.org
#api_id = 14730333
#api_hash = '07be164bbc0521510c9c86d258b9da8e'

api_id = 25315069
api_hash = '419b7cd9f055a855ffd2f06948ab882e'

replies = ['Go', 'gg', 'g', '+', '++', 'я', 'беру', 'готов', 'сделаю'];

# The first parameter is the .session file name (absolute paths allowed)
#with TelegramClient('anon', api_id, api_hash) as client:
#    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))

client = TelegramClient('anon', api_id, api_hash)

#@client.on(events.NewMessage(chats=[5427745665,1001417778781,1001778520278],pattern=r'.*\d?\d:\d\d-\d?\d:\d\d'))
@client.on(events.NewMessage(chats=[1001417778781],pattern=r'\u2757\d?\d:\d\d\ ?-\ ?\d?\d:\d\d\ \ ?\d'))
#@client.on(events.NewMessage(chats=[1001417778781]))

message_hashes = []

async def my_event_handler(event):
#  print( event)
  if 474122935 == event.from_id.user_id:           # Alexander
#  if 358409707 == event.from_id.user_id or 474122935 == event.from_id.user_id:           # Valery
#    if 'hello' in event.raw_text or 'good' in event.raw_text:
#        await event.reply('hi!')
        print(event)

#        await event.forward_to(5427745665)
        await event.forward_to(5569117599) # bot

#        if re.search( r'samanelis1', str(event.raw_text), re.IGNORECASE) or \
#          re.search( r'bifrost1', str(event.raw_text), re.IGNORECASE) or \
#          re.search( r'odysseus1', str(event.raw_text), re.IGNORECASE):
#        if re.search( r'RHEL\s?\+\s?Veritas', str(event.raw_text), re.IGNORECASE):
        if re.search( r'RHEL\s?\+\s?Veritas', str(event.raw_text), re.IGNORECASE) or \
          re.search( r'АУ АС', str(event.raw_text), re.IGNORECASE):
#          await event.forward_to(5569117599) # bot
          print('Matching work description')

          z = re.match( r'\u2757(\d?\d):\d\d\ ?-\ ?\d?\d:\d\d\ \d', str(event.raw_text))
          if z and (
            z.groups()[0] == "0" or
            z.groups()[0] == "00" or
            z.groups()[0] == "01" or
            z.groups()[0] == "1" or
            z.groups()[0] == "02" or
            z.groups()[0] == "2" or
            z.groups()[0] == "23" or
            z.groups()[0] == "22" or
            z.groups()[0] == "21"):
            print('Convenient time')
#            await event.reply('go') # auto reply

            hash = hashlib.md5(event.raw_text.encode('utf-8')).hexdigest()
            print('New message hash', hash)
            match_found = False
            for h in message_hashes:
              print('Compare to existing hash', h)
              if hash == h:
                print('Skipping matched hash', h, hash)
                match_found = True
                break
            if match_found is False:
              print('Adding new hash and autoreply')
              message_hashes.append(hash)
              await event.reply(random.choice(replies)) # auto reply

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

