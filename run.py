#!/usr/bin/env python3

import discord
import os
import sys
import json
import asyncio
import logging
import websrv
import shutil
from discord.ext import commands
from _thread import start_new_thread

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
	if discord.opus.is_loaded():
		return True
	for opus_lib in opus_libs:
		try:
			discord.opus.load_opus(opus_lib)
			return
		except OSError:
			pass
	raise RuntimeError('Could not load an opus lib.')

conf = None

def loadConfig():
	global conf
	with open('bot.json') as data:
		conf = json.load(data)

loadConfig()
currentVoiceChannel = 0
voice = None
player = None
volume = conf['volume']
admins = conf['admins']
blacklist = conf['blacklist']
modguild = conf['modGuildID']
modchannel = conf['modChannelID']
commandNames = None

def saveConfig():
	global conf
	global volume
	global commandChannel
	global whiteList
	global admins
	conf['volume'] = volume
	conf['admins'] = admins
	with open('bot.json', 'w') as data:
		json.dump(conf, data)
	loadConfig()

client = commands.Bot(command_prefix=conf['invoker'])

def getAllCommandNames():
	global commandNames
	names = []
	for command in client.commands:
		names.append(command.name)
	commandNames = names

@client.event
async def on_ready():
	logger.info("bot started")
	await client.change_presence(activity=discord.Game(name='sounds'))
	load_opus_lib()
	getAllCommandNames()

@client.event
async def on_command_error(ctx, exception):
	await ctx.message.channel.send("Il y a eu un problème lors de l'exécution de cette commande.")

@client.command()
async def removeadmin(ctx):
	global admins
	if ctx.message.author.id == conf['ownerID']:
		try:
			removedUsers = []
			notRemovedUsers = []
			for user in ctx.message.mentions:
				if user.id in admins:
					admins.remove(user.id)
					removedUsers.append(user.mention)
				else:
					notRemovedUsers.append(user.mention)
			successMessage = "Merci de mentionner un utilisateur à supprimer"
			if len(removedUsers) > 0:
				successMessage += "Removed " + ", ".join(removedUsers) + " as admin."
			if len(notRemovedUsers) > 0:
				successMessage += ", ".join(notRemovedUsers) + " weren't admin in the first place :smile:"
			saveConfig()
			await ctx.message.channel.send(successMessage)
		except Exception as e:
			logger.debug(str(e))
			await ctx.message.channel.send("Something went wrong.")
	else:
		await ctx.message.channel.send("Only the owner can remove an admin.")

@client.command()
async def addadmin(ctx):
	global admins
	if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
		try:
			addedUsers = []
			notAddedUsers = []
			for user in ctx.message.mentions:
				if not user.id in admins:
					admins.append(user.id)
					addedUsers.append(user.mention)
				else:
					notAddedUsers.append(user.mention)
			successMessage = "Utilisateur incorrect, veuillez mentionner un utilisateur."
			if len(addedUsers) > 0:
				successMessage = "J'ai ajouté " + ", ".join(addedUsers) + " à la liste des administrateurs."
			if len(notAddedUsers) > 0:
				successMessage += ", ".join(notAddedUsers) + " sont déjà administrateurs."
			saveConfig()
			await ctx.message.channel.send(successMessage)
		except Exception as e:
			logger.error(str(e))
			await ctx.message.channel.send("Une erreur est survenue.")
	else:
		await ctx.message.channel.send("Seulement un administrateur peut ajouter d'autres administtrateurs.")


@client.command(name="remove")
async def remove_sound(ctx):
	global commandChannel
	channel = ctx.message.channel
	if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
		try:
			if not os.path.isdir("deleted_sounds"):
				os.makedirs("deleted_sounds")
				removedOne = False
			for format in conf['fileformats']:
				if os.path.exists("sounds/" + ctx.message.content[len(conf['invoker'] + "remove "):] + format):
					removedOne = True
					os.rename("sounds/" + ctx.message.content[len(conf['invoker'] + "remove "):] + format, "deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "remove "):] + format)
					await channel.send("Son supprimé avec succès.")
					break
			if not removedOne:
				await channel.send("Ce son n'existe pas !")
		except Exception as e:
			logger.debug(str(e))
			await channel.send("Quelque chose à échoué...\n")
	else:
		await channel.send("Seulement les administrateurs du bot peuvent supprimer et ajouter des sons.")

@client.command(name="restore")
async def restore_sound(ctx):
	global commandChannel
	channel = ctx.message.channel
	if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
		try:
			restoredOne = False
			for format in conf['fileformats']:
				if os.path.exists("deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format):
					restoredOne = True
					os.rename("deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format, "sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format)
					await channel.send("Son restoré avec succès.")
					break
			if not restoredOne:
				await channel.send("Ce son n'existe pas.")
		except Exception as e:
			logger.debug(str(e))
			await channel.send("Une erreur est survenue.\n")
	else:
		await channel.send("Seulement les administrateurs du bot peuvent gérer les sons.")

@client.command(name="clearremovedsounds")
async def clear_sounds(ctx):
	global commandChannel
	channel = ctx.message.channel
	if ctx.message.author.id == conf['ownerID']:
		try:
			shutil.rmtree("deleted_sounds")
			await channel.send("Removed all sounds in the \"deleted_sounds\" directory.")
		except Exception as e:
			logger.debug(str(e))
			await channel.send("Something went wrong. Please try again.")
	else:
		await channel.send("This command can only be used by the owner!")


@client.command()
async def list(ctx):
	channel = ctx.message.channel
	if ctx.message.author.dm_channel == None:
		try:
			await ctx.message.author.create_dm()
		except Exception as e:
			logger.debug(str(e))
	try:
		f = []
		dirs = os.listdir("sounds/")
		for file in dirs:
			f.append(conf['invoker'] + file[:file.rfind('.')])
		f.sort()
		fs = "\n".join(f)
		embed = discord.Embed(title="Utilisez les commandes suivantes pour jouer des sons:", description=fs, color=0xcc2f00)
		await channel.send(content=None, tts=False, embed=embed)
	except Exception as e:
		logger.debug(str(e))

@client.command(name="listdeleted")
async def list_deleted_sounds(ctx):
	global commandChannel
	channel = ctx.message.channel
	if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
		if ctx.message.author.dm_channel == None:
			try:
				await ctx.message.author.create_dm()
			except Exception as e:
				logger.debug(str(e))
			if not os.path.isdir("deleted_sounds"):
				os.makedirs("deleted_sounds")
			try:
				f = []
				dirs = os.listdir("deleted_sounds/")
				for file in dirs:
					f.append(file[:file.rfind('.')])
					f.sort()
				fs = "\n".join(f)
				if fs == "":
					title = "Aucun son n'a été supprimé."
				else:
					title = "Les sons suivants peuvent être restorés:"
					embed = discord.Embed(title=title, description=fs, color=0xcc2f00)
					await channel.send(content=None, tts=False, embed=embed)
			except Exception as e:
				logger.debug(str(e))

@client.command()
async def stop(ctx):
	global voice
	if voice != None:
		voice.stop()

@client.command(name="volume")
async def set_volume(ctx):
	global volume
	channel = ctx.message.channel
	try:
		v = float(ctx.message.content[ctx.message.content.find(' ')+1:])
		v = int(v)
		if v < 1:
			volume = 0.01
		elif v > 100:
			volume = 1.0
		else:
			volume = float(v/100)
		saveConfig()
		await channel.send(content="Changed the volume to " + str(int(volume*100)))
	except Exception as e:
		await channel.send(content="There was an error setting the volume.")
		logger.debug(str(e))

def getListOfAliases():
	f = []
	dirs = os.listdir("sounds/")
	for file in dirs:
		f.append(file[:file.rfind('.')])
	return f

@client.command(name="ban")
async def ban_user(ctx, arg):
	global blacklist
	if len(str(arg)) == 18:
		if int(arg) not in conf['blacklist']:
			blacklist.append(int(arg))
			await ctx.send("L'identifiant **"+str(arg)+"** a été ajouté à la liste noire !")
		else:
			await ctx.send("L'identifiant que vous avez donné est déjà dans la liste noire !")
	else:
		await ctx.send("Ceci n'est pas un identifiant valide !")

@client.command(name="unban")
async def unban_user(ctx, arg):
	global blacklist
	if len(str(arg)) == 18:
		if int(arg) in conf['blacklist']:
			blacklist.remove(int(arg))
			await ctx.send("L'identifiant **"+str(arg)+"** a été supprimé de la liste noire !")
		else:
			await ctx.send("L'identifiant que vous avez donné n'est pas dans la liste noire !")
	else:
		await ctx.send("Ceci n'est pas un identifiant valide !")


@client.command(aliases=getListOfAliases())
async def play_sound(ctx):
	global currentVoiceChannel
	global voice
	global volume
	logger.info("play sound received")

	channel = ctx.message.channel
	guild = None
	for guilds in client.guilds:
		guild = guilds
		vchannel = guild.get_member(ctx.message.author.id).voice.channel
	perm = None
	if vchannel != None:
		perm = vchannel.permissions_for(vchannel.guild.me).connect
	else:
		perm = False
	if vchannel and perm:
		try:
			if voice != None:
				voice.stop()
			if currentVoiceChannel != vchannel:
				if voice != None:
					await voice.disconnect()
				voice = await vchannel.connect()
				currentVoiceChannel = vchannel
				for format in conf['fileformats']:
					if os.path.exists("sounds/" + ctx.message.content[len(conf['invoker']):] + format):
						sourceToPlay = discord.FFmpegPCMAudio('sounds/' + ctx.message.content[len(conf['invoker']):] + format)
						sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
						sourceToPlay.volume = volume
						voice.play(sourceToPlay)
						break
		except Exception as e:
			logger.debug("error while playing sound" + str(e))
	else:
		await channel.send("Vous n'êtes pas connecté dans un salon vocal, ou je n'ai pas la permission de m'y connecter.")

@client.event
async def on_voice_state_update(member,before,after):
	global voice
	global currentVoiceChannel
	global volume
	user = member
	perm = None
	if after.channel != None:
		perm = after.channel.permissions_for(after.channel.guild.me).connect
	else:
		perm = False

	if user != client.user and after.channel != None and perm and after.channel != before.channel:
		try:
			if voice != None:
				voice.stop()

			if currentVoiceChannel != after.channel:
				if voice != None:
					await voice.disconnect()
				logger.debug("joining voice channel")
				voice = await after.channel.connect()
				currentVoiceChannel = after.channel

			for format in conf['fileformats']:
				if os.path.exists("sounds/" + user.name + format):
					sourceToPlay = discord.FFmpegPCMAudio('sounds/' + user.name + format)
					sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
					sourceToPlay.volume = volume
					voice.play(sourceToPlay)
					break
		except Exception as e:
			logger.debug("error in playing join sound" + str(e))

@client.event
async def on_message(message):
	global commandNames
	if not message.author.bot:
		channel = message.channel
		if type(message.channel) is discord.DMChannel:
			if message.author.id not in conf['blacklist']:
				if len(message.attachments) > 0:
					logger.debug("attachement detected")
					if message.attachments[0].filename[message.attachments[0].filename.rfind('.'):] in conf['fileformats']:
						exists = False
						for format in conf['fileformats']:
							if os.path.exists("sounds/" + message.attachments[0].filename[:message.attachments[0].filename.rfind('.')] + format):
								exists = True

						if not exists:
							logger.debug("trying to save new sound")
							try:
								chn = client.get_guild(int(modguild)).get_channel(int(modchannel))
								sender = str(message.author)
								filename = str(message.attachments[0].filename)
								url = str(message.attachments[0].url)
								await chn.send("Un nouveau son a été proposé !\nUtilisateur : **"+sender+"**\n Nom du fichier: **"+filename+"**\nLien vers le fichier : "+url+"")
								await message.attachments[0].save("sounds/" + message.attachments[0].filename)
								client.get_command("play_sound").aliases.append(message.attachments[0].filename[:message.attachments[0].filename.rfind('.')])
								ncmd = client.get_command("play_sound")
								client.all_commands[message.attachments[0].filename[:message.attachments[0].filename.rfind('.')]] = ncmd
								logger.debug("file successfully received")
								await channel.send("Le son est désormais en ajouté à la liste !\nMerci de votre participation !")
							
							except Exception as e:
								logger.error(str(e))
								await channel.send("Une erreur est survenue, merci de réessayer.")
						else:
							await channel.send("Désolé, mais ce son existe déjà.")
					else:
						reply = "Format invalide. Les formats acceptés sont :\n"
						reply += ", ".join(conf['fileformats'])
						await channel.send(reply)
						logger.debug("invalid filetype")
				else:
					await client.process_commands(message)
			else:
				await channel.send("Désolé, mais vous êtes dans la liste noire.\nSi vous pensez que c'est une erreur, veuillez contacter un administrateur")
		else:
			if len(message.attachments) > 0:
				pass
			else:
				if message.content.startswith(conf['invoker']):
					if message.author.id not in conf['blacklist']:
						await client.process_commands(message)
					else:
						await channel.send("Désolé, mais vous êtes dans la liste noire.\nSi vous pensez que c'est une erreur, veuillez contacter un administrateur")
					
def srv_sound(sound):
	global voice
	logger.info("message received")
	if voice != None:
		voice.stop()
		if voice.is_connected():
			for format in conf['fileformats']:
				if os.path.exists("sounds/" + sound + format):
					sourceToPlay = discord.FFmpegPCMAudio('sounds/' + sound + format)
					sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
					sourceToPlay.volume = volume
					voice.play(sourceToPlay)

def srv_volume(vol):
	global volume
	try:
		v = int(vol)
		if v < 1:
			volume = 0.01
		elif v > 100:
			volume = 1.0
		else:
			volume = float(v/100)
		logger.info("set volume to" + str(volume))

	except Exception as e:
		logger.debug(str(e))

websrv.play_sound=srv_sound
websrv.set_volume=srv_volume
start_new_thread(websrv.app.run, (conf['host'], conf['port']))
client.run(conf['token'])
