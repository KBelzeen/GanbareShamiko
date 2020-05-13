# GanbareShamiko
A simple Discord.py bot that looks for new manga chapters via the MangaDex API once every hour and notifies you once it finds any.

## Requirements
Python 3.6+

discord.py 1.3.3+

requests 2.21.0

Earlier versions might also work, but haven't been tested.

## Running your own instance
Simply clone this repository, add your bot's token to the **auth.json** file, and run the application with `python mangadex.py`

## Using the bot

Once the bot is running, simply add as many manga as you want via the commands. Once per hour, the bot will retrieve chapter information from the API, and will send you a DM containing the links to all new chapters it could find in your notification list.

Because it makes many API calls at startup in order to regenerate the chapter list, it might take a while for the bot to fully start if your manga list is large.

## Commands

All commands are case-insensitive

* **;addmanga <manga ID/link>**
  
   Adds a manga to the bot's database if not present, then adds it to your notification list.

* **;removemanga <manga ID/link>**
  
  Removes a manga from your notification list.

* **;mylist**

  Shows you the titles of all manga in your notification list.

* **;lastchapter <manga ID/link>**
  
  Shows you the link to the latest chapter for any given manga.
