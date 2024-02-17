import configparser
import discord


config = configparser.ConfigParser()
config.read('config.ini')

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
  if message.guild.id == int(config['discord']['source_guild']) and message.channel.id == int(config['discord']['source_channel']):
    # Send the message to the destination guild, channel, thread
    guild = client.get_guild(int(config['discord']['destination_guild']))
    thread = await guild.fetch_channel(int(config['discord']['destination_thread']))
    print(message.content)
    await thread.send(message.content)

if __name__ == '__main__':
  client.run(config['discord']['token'])