import configparser
import discord
import pathlib
import os
import logging


logger = logging.getLogger('script')

# From https://github.com/Rapptz/discord.py
class _ColourFormatter(logging.Formatter):
  LEVEL_COLOURS = [
    (logging.DEBUG, '\x1b[40;1m'),
    (logging.INFO, '\x1b[34;1m'),
    (logging.WARNING, '\x1b[33;1m'),
    (logging.ERROR, '\x1b[31m'),
    (logging.CRITICAL, '\x1b[41m'),
  ]

  FORMATS = {
    level: logging.Formatter(
      f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s',
      '%Y-%m-%d %H:%M:%S',
    )
    for level, colour in LEVEL_COLOURS
  }

  def format(self, record):
    formatter = self.FORMATS.get(record.levelno)
    if formatter is None:
      formatter = self.FORMATS[logging.DEBUG]

    if record.exc_info:
      text = formatter.formatException(record.exc_info)
      record.exc_text = f'\x1b[31m{text}\x1b[0m'

    output = formatter.format(record)

    record.exc_text = None
    return output

handler = logging.StreamHandler()
handler.setFormatter(_ColourFormatter())
logger.setLevel(logging.INFO)
logger.addHandler(handler)

settings = {}

if pathlib.Path('config.ini').exists() == True:
  settings['type'] = 'config.ini'
  config = configparser.ConfigParser()
  config.read('config.ini')
  settings['id'] = config['discord']['id']
  settings['token'] = config['discord']['token']
  settings['source_guild'] = int(config['discord']['source_guild'])
  settings['source_channel'] = int(config['discord']['source_channel'])
  settings['destination_guild'] = int(config['discord']['destination_guild'])
  settings['destination_thread'] = int(config['discord']['destination_thread'])
elif 'DISCORD_ID' in os.environ:
  settings['type'] = 'environment variables'
  settings['id'] = os.environ['DISCORD_ID']
  settings['token'] = os.environ['DISCORD_TOKEN']
  settings['source_guild'] = int(os.environ['DISCORD_SOURCE_GUILD'])
  settings['source_channel'] = int(os.environ['DISCORD_SOURCE_CHANNEL'])
  settings['destination_guild'] = int(os.environ['DISCORD_DESTINATION_GUILD'])
  settings['destination_thread'] = int(os.environ['DISCORD_DESTINATION_THREAD'])
else:
  logger.log(logging.INFO, "config.ini missing and environment variables not set. Exiting.")
  exit()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.log(logging.INFO, f'Logged in as {client.user.name} ({client.user.id})')

@client.event
async def on_message(message: discord.Message):
  # Check if the message was in config[discord][source_guild] and config[discord][source_channel]
  if message.guild.id == settings['source_guild'] and message.channel.id == settings['source_channel']:
    # Send the message to the destination guild, channel, thread
    guild = client.get_guild(settings['destination_guild'])
    thread = await guild.fetch_channel(settings['destination_thread'])
    await thread.send(f"```md\n{message.content}```")

if __name__ == '__main__':
  logger.log(logging.INFO, f"Using {settings['type']} for configuration.")
  client.run(settings['token'])