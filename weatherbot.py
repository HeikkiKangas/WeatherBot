# Works with Python 3.6 testing
# master test

import os
import asyncio
from discord.ext.commands import Bot
from weather_stations import WeatherStations

BOT_PREFIX = ("?", "!")
TOKEN = os.environ.get("TOKEN")

client = Bot(command_prefix=BOT_PREFIX)
ws = WeatherStations()

@client.command()
async def sää(*, city = 'Tampere'):
    city_split = city.strip().split(' ')
    capitalized_names = []
    for name in city_split:
        capitalized_names.append(name.capitalize())
    city_capitalized = " ".join(capitalized_names)
    try:
        weather = ws.get_weather(city_capitalized)
    except:
        await client.say("Haulla %s ei löytynyt säätietoja." % city_capitalized)
        return
    if weather.has_wind():
        await client.say("%s\nLämpötila: %s c\nKosteus: %s %%\nKastepiste: %s c\nTuuli: %s m/s\nTuulensuunta %s" % (city_capitalized, weather.temperature, weather.humidity, weather.dew_point, weather.wind_speed, weather.wind_direction))
    else:
        await client.say("%s\nLämpötila: %s c\nKosteus: %s %%\nKastepiste: %s c" % (city_capitalized, weather.temperature, weather.humidity, weather.dew_point))

@client.command()
async def asemat(city):
    city_capitalized = city.capitalize().strip()
    areas = ws.get_stations(city_capitalized)
    if len(areas) == 0:
        response = "Kaupungissa %s ei ole sääasemaa." % (city_capitalized)
    else:
        response = "Sääasemat %s:\n" % (city_capitalized)
        for area in areas:
            response += "\t\t- %s\n" % (area.capitalize())
    await client.say(response)


@client.event
async def on_ready():
    await client.change_presence(game=None,  status=None, afk=False)
    print("Logged in as " + client.user.name)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
