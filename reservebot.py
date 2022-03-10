from email import header
from multiprocessing.connection import Client
from wsgiref.headers import Headers
import discord
import requests
import json
import os
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from PIL import Image, ExifTags

# define static api stuff and image manipulation
api_link = "https://impermanent.digital/api/idreamer/reserve"
headers = {'Content-type': 'application/json'}
image2 = 0

# define static discord stuff
token = "OTI3OTcxNDkyMTQ5NDYwOTkz.YdR-zA.ohnB6dPvZ1rkg2ayYe8gsXa26KQ"
bot = commands.Bot(command_prefix='!', activity= discord.Activity(type=discord.ActivityType.watching, name="for !reserve \U0001F973"))
bot.remove_command('help')

# show in console that bot is running and connected
@bot.event
async def on_ready():
    print("!Reservebot(tm) is online and ready to roll")

# better help command
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title ='!Reservebot usage',
        description ='Welcome to the Reservebot. Intended usage is stated below',
        color =discord.Colour.green()
    )

    embed.set_thumbnail(url='https://mint.impermanent.digital/idreamer/4110.png')
    embed.add_field(
        name='!reserve',
        value="Please use the reply function on the image you want to Reserve, if you've created the image you will recieve a DM with a link to our Mint site.",
        inline='true'
    )

    await ctx.send(embed=embed)

@bot.command()
async def mint(ctx):
    # finds image the user is referencing and downloads the image
    path = ctx.message.reference.resolved.attachments[0].url
    image2 = requests.get(path, allow_redirects=True)
    open("images/" + path.split('/')[-1], 'wb').write(image2.content)
    img = Image.open("images/" + path.split('/')[-1], 'r')
    #try 

    # Check if there is an image in the message the !mint command is replying to.
    if ctx.message.reference.resolved is None or len(ctx.message.reference.resolved.attachments) < 1:
        await ctx.send("Sorry, I was unable to mint. Either is this not a image or we've encountered an error")
    elif img.text['Ismintable'] is None or img.text['Ismintable'] == 'No' :
        await ctx.send('Sorry this image was unable to be minted!')
    elif img.text['Singleauthor'] is None or img.text['Singleauthor'] == 'No' or len(ctx.message.reference.resolved.mentions) == 0 or not ctx.message.reference.resolved.mentions[0] == ctx.message.author:
        await ctx.send("Oops! You can only mint works that you have made, try again" )
    else:
        try:
            author = str(await bot.fetch_user(img.text["Author"]))
            payload = { "url": path,
                        "Author" : author.split('#')[0]
                        }
            #print(author.split('#')[0])
            r = requests.post(api_link, data=json.dumps(payload), headers=headers)

            embed =discord.Embed(
                title='Click here to finalize the reserve!',
                url=r.json()['mintUrl'], 
                description ="Thank you for reserving through Impermanent.Digital's Reservebot" + '\U00002122', 
                color=discord.Color.dark_orange()
                )
            embed.set_thumbnail(url=path)

            await ctx.message.author.send(embed=embed)
            await ctx.send(content="Check your DMs \U0001F916")
        except discord.errors.Forbidden:
            await ctx.send(content=f"Sorry {ctx.author.mention} please open your DMs in User Settings > Privacy & Safety and check your privacy settings for the sever!")
    os.remove("images/" + path.split('/')[-1])


bot.run(token)
