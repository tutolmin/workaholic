#!/usr/bin/python3 -u

from telethon import TelegramClient, events

# Use your own values from my.telegram.org
#api_id = 14730333
#api_hash = '07be164bbc0521510c9c86d258b9da8e'

api_id = 25315069
api_hash = '419b7cd9f055a855ffd2f06948ab882e'
bot_token = '5569117599:AAEa8rwinzdBB5fSDGg1zJOXha13938CC-0'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond('Hi!')
    raise events.StopPropagation

@bot.on(events.NewMessage)
async def echo(event):
    """Echo the user message."""
#    await event.respond( 'Message has been forwarded successfully.')
#    await event.respond(event.text)
#    await bot.send_message(-616817594, event.text)
    await event.forward_to(-616817594)

def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()

