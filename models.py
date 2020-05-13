import discord
from discord.ext import commands

import requests

import json

TAG_STATUS = 'status'

TAG_MANGA = 'manga'
TAG_TITLE = 'title'

TAG_LANG = 'lang_code'
TAG_CH = 'chapter'
TAG_VOL = 'volume'
LANG = 'gb'

class MangaDatabase():
    def __init__(self):
        self.mangaList = []
        
    def __getitem__(self, key):
        return self.mangaList[key]
    
    def __bool__(self):
        return self.mangaList != []
    
    def addManga(self, mangaID):
        if self.fetchManga(mangaID):
            return True
            
        manga = Manga(mangaID)
        if hasattr(manga, 'title'):
            self.mangaList.append(manga)     
            return True
        return False
        
    def removeManga(self, manga):
        try:
            self.database.remove(manga)
            return True
        except:
            return False

    def fetchManga(self, mangaID):
        for manga in self.mangaList:
            if manga.mangaID == mangaID:
                return manga
        return None
        
    def clearNewChapters(self):
        for manga in self.mangaList:
            if manga.hasNewChapters:
                manga.chapters = manga.getChapters()

class Chapter():
    def __init__(self, chapterID, volume, chapter):
        self.chapterID = chapterID
        self.volume = volume
        self.chapter = chapter
        
    def __bool__(self):
        return True
        
    def getLink(self):
        return 'https://mangadex.org/chapter/{}'.format(self.chapterID)

class Manga():
    def __init__(self, mangaID):
        self.mangaID = mangaID
        mangaData = requests.get('https://mangadex.org/api/manga/{}'.format(self.mangaID))
        if mangaData.status_code != 200 or mangaData.json()[TAG_STATUS] == 'Manga ID does not exist.':
            return
        self.mangaData = mangaData.json()
        self.title = self.getTitle()    
        self.chapters = self.getChapters()
        self.hasNewChapters = None

    def __bool__(self):
        return self.mangaID is not None

    def getTitle(self):
        return self.mangaData[TAG_MANGA][TAG_TITLE]

    def getChapters(self):
        bufferList = []
        chapterList = self.mangaData[TAG_CH]
        for chapter in chapterList:
            if chapterList[chapter][TAG_LANG] == LANG:
                bufferList.append(Chapter(chapter, chapterList[chapter][TAG_VOL], chapterList[chapter][TAG_CH]))
        return bufferList
    
    def checkNewChapters(self):
        self.mangaData = requests.get('https://mangadex.org/api/manga/{}'.format(self.mangaID)).json()
        self.hasNewChapters = len(self.getChapters()) != len(self.chapters)
        
class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.userList = self.loadData()
        self.database = MangaDatabase()
        for user in self.userList.keys():
            for mangaID in self.userList[user]:
                self.database.addManga(mangaID)
        super().__init__(*args, **kwargs)
        
    def loadData(self):
        with open('data.json', 'r', encoding='utf-8') as inFile:
            return json.load(inFile)
        
    def saveData(self):
        with open('data.json', 'w', encoding='utf-8') as outFile:
            json.dump(self.userList, outFile, indent=2)
            
    def addManga(self, user, mangaID):
        if user not in self.userList:
            self.userList[user] = []
        
        if self.database.addManga(mangaID):
            if mangaID in self.userList[user]:
                return False
            self.userList[user].append(mangaID)
            return True
        return False
        
    def removeManga(self, user, mangaID):
        if user in self.userList:
            if mangaID in self.userList[user]:
                self.userList[user].remove(mangaID)
                return True
        return False