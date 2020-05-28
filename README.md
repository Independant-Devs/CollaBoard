# CollaBoard

[![Python](https://img.shields.io/badge/python-3.5%2C%203.6-blue.svg?style=flat-square)](https://www.python.org/downloads/)

CollaBoard permet de créer une soundboard collaborative sur votre serveur Discord. Il a été créé en [Python](https://www.python.org "Python homepage") 3.5+, en utilisant la librairie [discord.py](https://github.com/Rapptz/discord.py).

## Installation

Pour installer le bot, vous devez :
* créer un compte de bot (Vous pouvez trouver un tutoriel [ici](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) :warning: Tutoriel en anglais !)
* installer la librairie discord.py (branche "rewrite" nécéssaire: `python -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]`)
* installer ffmpeg (par exmple sur Debian: `[sudo] apt install ffmpeg`; Vérifiez qu'il est dans la variable PATH: `which ffmpeg`)
* installer flask (`python -m pip install flask`)
* modifier le fichier de configuration. Changez les paramètres désirés et renommez le fichier en `bot.json`.

Et c'est tout :smile:. :warning: **Ce bot a été créé pour être utiliser sur UN seul serveur par instance** :warning:

## Utilisation
Vous pouvez ajouter des sons en les envoyant au bot en MP. Vous pouvez les jouer avec les commandes disponibles ou avec l'interface web qui est située sur `0.0.0.0:8080` par défaut. Utilisez la commande `help` pour voir les commandes disponibles.

Un système de liste noire est disponible. Le propriétaire (N'oubliez pas de le définir) peut ajouter des administrateurs qui peuvent bannir des utilisateurs de l'utilisation du bot. 

## Configuration 
Le fichier de configuration dispose de plusieurs valeurs obligatoires :
* la valeur `token` qui doit être remplacée par le token de votre bot
* la valeur `invoker` qui correspond au préfixe utilisé pour les commandes
* la valeur `ownerID` doit contenir votre identifiant unique (Activez le mode développeur sur Discord, cliquez droit sur votre nom, puis "Copier l'identifiant")
* la valeur `modGuildID` doit contenir l'identifiant de votre serveur
* la valeur `modChannelID` doit contenir l'identifiant d'un salon textuel dans votre serveur.

## Contribution
Vous pouvez contribuer à l'amélioration de ce bot en faisant un "fork" et en ouvrant une "pull request". Toute contribution est bienvenue, et tous les contributeurs seront listés.




