from models import *

from discord.ext import tasks
from concurrent.futures import ThreadPoolExecutor

import time
import asyncio

import json

with open('auth.json', 'r') as auth:
    TOKEN = json.load(auth)['TOKEN']
GOOD_EMOJI = '👍'
BAD_EMOJI ='👎'

bot = Bot(command_prefix = ';', case_insensitive=True)

@bot.event
async def on_ready():
    print('------')
    print(time.strftime('%m/%d/%Y, %H:%M:%S - Logged in as {0}'.format(bot.user.name)))
    
@tasks.loop(hours=1)
async def chapterUpdate():
    for manga in bot.database.mangaList:
        await bot.loop.run_in_executor(ThreadPoolExecutor(), manga.checkNewChapters)
    
    for userID in bot.userList:
        user = bot.get_user(int(userID))
        
        message = ''
        for mangaID in bot.userList[userID]:
            manga = bot.database.fetchManga(mangaID)
            if manga and manga.hasNewChapters:
                for chapter in manga.getChapters()[-len(manga.chapters) - 1::-1]:
                    message += f'{manga.title}'
                    if chapter.volume or chapter.chapter:
                        message += ' - '
                    if chapter.volume:
                        message += f'Volume {chapter.volume}'
                    if chapter.chapter:
                        message += f'Chapter {chapter.chapter}'
                    message += f' - {chapter.getLink()}\n'
        if message:
            message = f'{user.name}, one or more manga in your list have received an update:\n' + message
            await user.send(message)
            
    bot.database.clearNewChapters()

@chapterUpdate.before_loop
async def chapterUpdateBefore():
    await bot.wait_until_ready()
    await asyncio.sleep(3600) # Wait an hour before starting the task so you don't call the update function literally right after starting the bot. Yes, this is stupid.

@tasks.loop(hours=24)
async def cleanMangaDatabase():
    isMangaInList = {manga:False for manga in bot.database}
    mangaList = []
    for user in bot.userList:   
        for manga in bot.database:
            if isMangaInList[manga]:
                continue
            isMangaInList[manga] = True
            
    dummyMangas = [manga for manga in isMangaInList.keys() if isMangaInList[manga] is False]
    for manga in dummyMangas:
        bot.database.removeManga(manga.mangaID)

@cleanMangaDatabase.before_loop
async def clearDatabaseBefore():
    await bot.wait_until_ready()

@bot.command()
async def addManga(ctx, mangaID):
    if 'http' in mangaID:
        mangaID = mangaID.split('/')[4]
    
    userID = str(ctx.author.id)
    if bot.addManga(userID, mangaID):
        await ctx.message.add_reaction(GOOD_EMOJI)
    else:
        await ctx.message.add_reaction(BAD_EMOJI)
        
    bot.saveData()
    
@bot.command()
async def removeManga(ctx, mangaID):
    if 'http' in mangaID:
        mangaID = mangaID.split('/')[4]
    
    userID = str(ctx.author.id)
    if bot.removeManga(userID, mangaID):
        await ctx.message.add_reaction(GOOD_EMOJI)
    else:
        await ctx.message.add_reaction(BAD_EMOJI)
    
    bot.saveData()
    
@bot.command()
async def myList(ctx):
    userID = str(ctx.author.id)
    if userID in bot.userList:
        msg = ''
        for mangaID in bot.userList[userID]:
            manga = bot.database.fetchManga(mangaID)
            if len(msg + manga.title + '\n') > 2000:
                await ctx.send(msg)
                msg = ''
            msg += manga.title + '\n'
        if msg:
            await ctx.send(msg)
        
@bot.command()
async def lastChapter(ctx, *, mangaID):
    if 'http' in mangaID:
        mangaID = mangaName.split('/')[4]
    manga = bot.database.fetchManga(mangaID)
    if manga:
        msg =f'Here is the latest {manga.title} chapter I could find: {manga.chapters[0].getLink()}'
    else:
        msg = 'Looks like this manga is not in my database. To save up on API calls, any mangas not in anyone\'s list will be removed from the database within 24 hours.'
    await ctx.send(msg)
    
@bot.command()
async def disconnect(ctx):
    await bot.close()
        
cleanMangaDatabase.start()
chapterUpdate.start()
bot.run(TOKEN)
