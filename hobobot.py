#!/usr/bin/python3

import discord
import asyncio
import os
import requests
import json
import yaml
import shodan
import random


#secrets = open("secrets.yml", "r")
#cfg = yaml.load(secrets)

#DISCORD_TOKEN = cfg['discord']['DISCORD_TOKEN']

QUOTE_FILE = "quotes.txt"
BASEPATH = '/Users/mahrens/Documents/BreachCompilation/BreachCompilation/data'

def getCoinbase(currency):
    buy = requests.get("https://api.coinbase.com/v2/prices/" + currency + "/buy")
    sell = requests.get("https://api.coinbase.com/v2/prices/" + currency + "/sell")
    if(sell.status_code != 200 or buy.status_code != 200):
        return "hey fuckers coinbase gave me a bad response, see: " + buy.text
    print (buy.text)
    print (sell.text)
    buyJson = json.loads(buy.text)
    sellJson = json.loads(sell.text)
    response = "**Coinbase** \n\tBuying " + buyJson['data']['base'] + " at " + buyJson['data']['amount'] + " in " + buyJson['data']['currency']
    response = response + '\n\tSelling ' + sellJson['data']['base'] + " at " + sellJson['data']['amount'] + " in " + sellJson['data']['currency']
    return(response)

def getBitfinex(currency):
    url = "https://api.bitfinex.com/v1/pubticker/" + currency + 'usd'
    response = requests.request("GET", url)
    data = json.loads(response.text)
    return("**Bitfinex** - Last sell price: " + data['last_price'])

def getCoindesk():
    coindesk = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    try:
        cdJson = json.loads(coindesk.text)
    except:
        cdJson = {}
    if('bpi' in cdJson):
        return("Coindesk current BTC price in USD: " + cdJson['bpi']['USD']['rate'])
    else:
        return("fuck you coindesk")

def getCoins(currency):
    if(currency.lower() == 'btc'):
        response = getCoinbase(currency + '-usd')
        response = response + "\n" + getCoindesk()
        response = response + "\n" + getBitfinex(currency)
        return response
    else:
        return(getCoinbase(currency[:3] + '-usd') + '\n' + getBitfinex(currency[:3]))

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

def shodanScan(ipaddr):
   api = shodan.Shodan(SHODAN_API_KEY)
   try:
      scanData = api.host(ipaddr)
   except:
      scanData = "some shitty error happened you fucked"
   if(isinstance(scanData, dict)):
      response = ipaddr
      if(isinstance(scanData['data'], list)):
         for item in scanData['data']:
            port = item.get('port', 'Unknown Port')
            product = item.get('product', 'Unknown Product')
            version = item.get('version', 'Unknown Version')
            response = response + '\n\t' + str(port) + ' / ' + product + ' / ' + version
      else:
         port = scanData['data'].get('port', 'Unknown Port')
         product = scanData['data'].get('product', 'Unknown Product')
         version = scanData['data'].get('version', 'Unknown Version')
         response = response + '\n\t' + str(port) + ' / ' + product + ' / ' + version
   else:
      response = scanData
   return response

def addQuotes(quote):
    f = open(QUOTE_FILE, 'r')
    for line in f.readlines():
        if line == quote:
            print("Quote already found, skipping")
            return("Quote found, doing nothing")
    f.close()
    f = open(QUOTE_FILE, 'a')
    f.write(quote + "\n")
    f.close()
    return("Quote added!")

def getQuote():
    f = open(QUOTE_FILE, 'r')
    data = f.readlines()
    if(len(data)==0):
        return("HEY I'M DRINKING HERE")
    print(str(len(data)))
    index = random.randint(0, len(data))
    return(data[index-1])

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
    elif message.content.startswith('!shodan'):
        items = message.content.split(" ")
        if(len(items)>1):
            output=shodanScan(items[1])
        else:
            output = "Error no IP submitted"
        await client.send_message(message.channel, output)
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
    elif message.content.find('hobo')>-1:
        await client.send_message(message.channel, getQuote())
    elif message.content.startswith("!addquote"):
        items = message.content.split(" ")
        if(len(items)>1):
            quote = " "
            if('!addquote' in items[1:]):
                response = "No recursive quotes for you Amin!"
            else:
                response = addQuotes(quote.join(items[1:]))
        else:
            response = "Bad syntax go home DrCruft"
        await client.send_message(message.channel, response)

client.run(DISCORD_TOKEN)
