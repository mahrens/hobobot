#!/usr/bin/python3

import discord
import asyncio
import os
import requests
import json
import yaml


secrets = open("secrets.yml", "r")
cfg = yaml.load(secrets)

DISCORD_TOKEN = cfg['discord']['DISCORD_TOKEN']
BASEPATH= cfg['pwdb']['PW_DB_PATH']

def getCoinbase(currency):
    buy = requests.get("https://api.coinbase.com/v2/prices/" + currency + "/buy")
    sell = requests.get("https://api.coinbase.com/v2/prices/" + currency + "/sell")
    buyJson = json.loads(buy.text)
    sellJson = json.loads(sell.text)
    response = "**Coinbase** \n\tBuying " + buyJson['data']['base'] + " at " + buyJson['data']['amount'] + " in " + buyJson['data']['currency']
    response = response + '\n\tSelling ' + sellJson['data']['base'] + " at " + sellJson['data']['amount'] + " in " + sellJson['data']['currency']
    return(response)

def getCoindesk():
    coindesk = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    cdJson = json.loads(coindesk.text)
    return("Coindesk current BTC price in USD: " + cdJson['bpi']['USD']['rate'])

def getCoins(currency):
    if(currency.lower() == 'btc'):
        response = getCoinbase(currency + '-usd')
        response = response + "\n" + getCoindesk()
        return response
    else:
        return(getCoinbase(currency + '-usd'))

def getPath(BASEPATH, email):
    print(type(email))
    tmpPath = os.path.join(BASEPATH, str(email[0]))
    if(os.path.isdir(tmpPath)):
        return getPath(tmpPath, email[1:])
    else:
        return tmpPath


def searchEmail(email):
    if(isinstance(email, bytes)):
        email = email.decode('utf-8')
    idxFile = getPath(BASEPATH, email)
    print(idxFile)
    searchFile = open(idxFile, 'r', errors='ignore')
    response = "Searched for email: " + email
    for line in searchFile.readlines():
        if(line.startswith(email)):
            response = response + '\n\t' + line.rstrip()
    return response


client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith("!email"):
        items = message.content.split(" ")
        for item in items:
            print(item)
        if(len(items)>1):
            output = searchEmail(items[1].encode('utf-8'))
        else:
            output = "Not enough arguments sent to email, use as !email emailaddr"
        print(output)
        await client.send_message(message.channel, output)
    elif message.content.startswith('!quote'):
        items = message.content.split(" ")
        if(len(items)>1):
            output = getCoins(items[1])
        else:
            output = "Error bad args"
        await client.send_message(message.channel, output)
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

client.run(DISCORD_TOKEN)