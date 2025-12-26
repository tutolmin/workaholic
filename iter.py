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

    for message in client.iter_messages(1001417778781,reverse=False):
      if message.photo and 474122935 == message.from_id.user_id:
        print('Image from Alex')
      if 474122935 == message.from_id.user_id:           # Alexander      
        print('Alex: ', message.date, ' ', message.message)
      if re.search( r'\u2757\d?\d:\d\d\ ?-\ ?\d?\d:\d\d\ \d', str(message.message)): 
        print(message.date, ' ', message.message)

        if re.search( r'RHEL\s?\+\s?Veritas', str(message.message), re.IGNORECASE) or \
          re.search( r'Veritas\s?\+\s?RHEL', str(message.message), re.IGNORECASE) or \
          re.search( r'АУ АС', str(message.message), re.IGNORECASE) or \
          re.search( r'перемонтировать', str(message.message), re.IGNORECASE):
          print(message.date, ' - matching work description')

          z = re.match( r'\u2757(\d?\d):\d\d\ ?-\ ?\d?\d:\d\d\ \d', str(message.message))
          if z and (
            z.groups()[0] == "0" or 
            z.groups()[0] == "00" or 
            z.groups()[0] == "1" or 
            z.groups()[0] == "01" or 
            z.groups()[0] == "2" or 
            z.groups()[0] == "02" or 
            z.groups()[0] == "23" or 
            z.groups()[0] == "22" or
            z.groups()[0] == "21"):
            print(message.date, ' - matched hour time', z.groups()[0])
#          if re.search( r'2(1|2|3)\:', str(message.message)):
#            print(message.date, ' - convenient time')
            hash = hashlib.md5(message.message.encode('utf-8')).hexdigest()
            print(message.date, 'New message hash', hash)
            match_found = False
            for h in message_hashes:
              print(message.date, h)
              if hash == h:
                print(message.date, 'Skipping matched hash', h, ' ', hash)
                match_found = True
                break
            if match_found is False:
              message_hashes.append(hash)

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

