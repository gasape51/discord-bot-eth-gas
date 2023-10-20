import os
import discord
from discord.ext import commands
from web3 import Web3
import asyncio
import requests
from dotenv import load_dotenv

load_dotenv()

# récupérer les variables d'environnement
HTTP_PROVIDER = os.getenv('HTTP_PROVIDER')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')


intents = discord.Intents.all()
client = commands.Bot(command_prefix='!',intents=intents)


w3 = Web3(Web3.HTTPProvider(HTTP_PROVIDER))
# adresse du contrat de chainlink pour le prix de l'eth en USD
price_feed_address = '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419'
abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "_aggregator", "type": "address"}
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "latestAnswer",
        "outputs": [{"internalType": "int256", "name": "", "type": "int256"}],
        "stateMutability": "view",
        "type": "function"
    }
]
contract = w3.eth.contract(address=price_feed_address, abi=abi)

# dictionnaire des seuils d'alerte par utilisateur
alert_thresholds = {}

# dictionnaire des booléens d'alerte par utilisateur
alert_triggered = {}

# dictionnaire des contextes par utilisateur
ctx_by_user_id = {}

async def alert_when_gas_price_below_threshold():
    while True:
        gas_price = w3.eth.gas_price*10**-9 # prix du gas en gwei
        for user_id, threshold in alert_thresholds.items():
            print(alert_triggered[user_id])
            print(threshold+0.15*threshold)
            if gas_price < threshold and not alert_triggered[user_id]:
                print(f"Le prix du gas est en dessous de {threshold} gwei : {round(gas_price, 2)}")
                await ctx_by_user_id[user_id].channel.send(f"<@{user_id}>```Le prix du gas sur ETH est en dessous de {threshold} Gwei : {round(gas_price, 1)}```")
                alert_triggered[user_id] = True
            elif gas_price >= threshold+0.15*threshold and alert_triggered[user_id]:
                alert_triggered[user_id] = False
        await asyncio.sleep(10) 

@client.event
async def on_ready():
    print('Bot prêt')
    client.loop.create_task(alert_when_gas_price_below_threshold())

@client.command()
async def get_sat(ctx):
    url="https://mempool.space/api/v1/fees/recommended"
    response = requests.get(url)
    data = response.json()
    await ctx.send(f"<@{ctx.author.id}>```Le prix du gas sur BTC est de :\nrapide : {data['fastestFee']} sats/vB (conseillé)\nmoyen : {data['halfHourFee']} sats/vB\nlent : {data['hourFee']} sats/vB```") 


@client.command()
async def get_gwei(ctx):
    eth_price_in_usd = contract.functions.latestAnswer().call() / 10 ** 8
    print('ETH/USD Price:', eth_price_in_usd)
    
    gas_price = w3.eth.gas_price*10**-9
    await ctx.send(f"<@{ctx.author.id}>```Le prix du gas sur eth est de {round(gas_price, 1)} Gwei.\nestimation d'un transfert d'ETH : {round(gas_price*21000*10**-9*eth_price_in_usd,2)} USD.\nestimation d'un swap sur uniswapV2 : {round(gas_price*152808*10**-9*eth_price_in_usd,2)} USD\nestimation d'un mint NFT : {round(gas_price*100000*10**-9*eth_price_in_usd,2)} USD (ATTENTION : à titre indicatif car le gas utilisé dépend du contrat)```")

# définir la commande pour choisir son seuil d'alerte
@client.command()
async def set_alert(ctx, threshold):
    if not threshold.isdigit():
        await ctx.send(f"```Le seuil d'alerte doit être un entier positif.```")
        return
    
    else :
        ctx_by_user_id[ctx.author.id] = ctx
        alert_thresholds[ctx.author.id] = int(threshold)
        alert_triggered[ctx.author.id] = False
        await ctx.send(f"```Seuil d'alerte défini à {threshold} Gwei.```")

@client.command()
async def get_alert(ctx):
    if(ctx.author.id not in alert_thresholds):
        await ctx.send(f"```Aucun seuil d'alerte défini.```")
    else :
        await ctx.send(f"```Seuil d'alerte actuel : {alert_thresholds[ctx.author.id]} Gwei.```")

@client.command()
async def del_alert(ctx):
    del alert_thresholds[ctx.author.id]
    del alert_triggered[ctx.author.id]
    del ctx_by_user_id[ctx.author.id]
    await ctx.send(f"```Seuil d'alerte supprimé.```")

@client.command()
async def help_gas(ctx):
    embed = discord.Embed(title="Liste des commandes disponibles :")
    embed.add_field(name="!get_sat", value="Affiche le prix de gas sur BTC.", inline=False)
    embed.add_field(name="!get_gwei", value="Affiche le prix actuel de gas sur ETH.", inline=False)
    embed.add_field(name="!set_alert [threshold]", value="Définit un seuil d'alerte pour la valeur du Gwei.", inline=False)
    embed.add_field(name="!get_alert", value="Affiche le seuil d'alerte actuellement défini pour la valeur du Gwei.", inline=False)
    embed.add_field(name="!del_alert", value="Supprime le seuil d'alerte actuellement défini pour la valeur du Gwei.", inline=False)
    await ctx.send(embed=embed)


# démarrer le bot
client.run(DISCORD_BOT_TOKEN)
