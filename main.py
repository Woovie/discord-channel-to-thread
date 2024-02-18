import configparser
import discord
import pathlib
import os


settings = {}

if pathlib.Path('config.ini').exists() == True:
  settings['type'] = 'config.ini'
  config = configparser.ConfigParser()
  config.read('config.ini')
  settings['id'] = config['discord']['id']
  settings['token'] = config['discord']['token']
  settings['source_guild'] = config['discord']['source_guild']
  settings['source_channel'] = config['discord']['source_channel']
  settings['destination_guild'] = config['discord']['destination_guild']
  settings['destination_thread'] = config['discord']['destination_thread']
# Otherise, use environment variables
elif 'DISCORD_ID' in os.environ:
  settings['type'] = 'environment variables'
  settings['id'] = os.environ['DISCORD_ID']
  settings['token'] = os.environ['DISCORD_TOKEN']
  settings['source_guild'] = int(os.environ['DISCORD_SOURCE_GUILD'])
  settings['source_channel'] = int(os.environ['DISCORD_SOURCE_CHANNEL'])
  settings['destination_guild'] = int(os.environ['DISCORD_DESTINATION_GUILD'])
  settings['destination_thread'] = int(os.environ['DISCORD_DESTINATION_THREAD'])
else:
  print("config.ini missing and environment variables not set. Exiting.")
  exit()

# Set up intents for reading message contents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):
  # Check if the message was in config[discord][source_guild] and config[discord][source_channel]
  if message.guild.id == settings['source_guild'] and message.channel.id == settings['source_channel']:
    # Send the message to the destination guild, channel, thread
    guild = client.get_guild(settings['destination_guild'])
    thread = await guild.fetch_channel(settings['destination_thread'])
    print(message.content)
    await thread.send(message.content)

if __name__ == '__main__':
  print(f"Loaded settings via {settings['type']}")
  client.run(settings['token'])