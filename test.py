import asyncio
import os
from datetime import datetime
import time
import schedule
import lunch_data
import hr_data
from fpdf import FPDF
import discord
import json
import sched

from config import DISCORD_TOKEN as TOKEN

async def send_yes_no_poll(channel):

    poll_text = f"**Présence :**\n"
    poll_text += ":white_check_mark: Je suis là\n\n"
    poll_text += ":x: Je ne suis pas là\n"

    await channel.send(poll_text)


def create_pdf_with_images(image_paths, output_path):

    pdf = FPDF()
    prix = None
    for image_path in image_paths:

        pdf.add_page()

        image_name = os.path.splitext(os.path.basename(image_path))[0] # récupérer le nom des images = nom des plats

        with open("products.json", 'r') as f:

            data = json.load(f)

            for product in data:

                if product['name'] == image_name:

                    prix = product['price']
                    description = product['description']
                    regime = product['x_regime_alimentaire']

        # titre en haut de l'image
        pdf.ln(5)
        pdf.set_font("Arial", style='B', size=30)
        pdf.cell(0, 10, txt=image_name, ln=True, align='C')
        pdf.ln(5)

        # image au milieu de la page
        pdf.image(image_path, x=pdf.w / 2 - 50, y=pdf.h / 2 - 50, w=100, h=100)
        pdf.ln(5)

        # titre en bas de l'image
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(0, 10, txt=description[3:-4], ln=True, align='C')
        pdf.cell(0, 10, txt=f"Prix : {prix} CHF ", ln=True, align='C')
        pdf.cell(0, 10, txt=regime, ln=True, align='C')

    pdf.output(output_path)


async def send_menu_with_images(member_dm_channel):

    image_folder = "images"

    # liste "images" contenant les chemins complets de tous les fichiers PNG dans le dossier spécifié par image_folder

    images = [os.path.join(image_folder, image) for image in os.listdir(image_folder) if image.endswith('.png')]
    create_pdf_with_images(images, 'menu.pdf')

    with open('menu.pdf', 'rb') as pdf_file:
        pdf_content = discord.File(pdf_file, filename='menu.pdf')

        await member_dm_channel.send("Voici le menu du jour :", file=pdf_content) # envoi du menu dans le canal

    os.remove('menu.pdf')

# vérification que le plat commandé par l'utilisateur existe bien
def verif_plat(user_reponse):

    with open("products.json", 'r') as f:

        data = json.load(f)

        for product in data:

            if product['name'] == user_reponse:

                return True

commande_traitee = False
nombre_utilisateurs_attendus = 0
offline = False

intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
commande = {}

now = datetime.now()

weekday = now.weekday()

# client.run(TOKEN)

# activation de la fonction (bot) tous les jours de semaine à 10 heures

# if 0 <= weekday <= 4 and now.hour == 10:

# Fonction pour gérer la déconnexion
@client.event
async def on_disconnect():
    print("Déconnexion du client Discord...")
    # await asyncio.gather(*asyncio.all_tasks())
    # await client.close()

@client.event
async def on_ready():

    global nombre_utilisateurs_attendus

    nombre_utilisateurs_attendus = 1

    # nombre_utilisateurs_attendus = len([member for member in guild.members if member.status == discord.Status.online and member != client.user])

    print('Bot connecté en tant que', client.user.name)

    print('------')

    # parcours de tous les serveurs ou le bot a été ajouté (ici un seul)

    for guild in client.guilds:

        nombre_utilisateurs_attendus = len(
            [member for member in guild.members if
             member.status == discord.Status.online and member != client.user])

        print(f"Nombre users : {nombre_utilisateurs_attendus}")

        print(f'Serveur: {guild.name}')

        # parcourir tous les membres du serveur

        for member in guild.members:

            # si le membre est online, on lui envoie l'action et on exclue le bot qui lui est toujours online

            if member.status == discord.Status.online and member != client.user:

                print(f'{member.name} est en ligne')

                try:

                    await member.send("Bonjour ! Veuillez confirmer votre présence : ")

                    # envoi du formulaire de présence

                    await send_yes_no_poll(member.dm_channel)

                    print(f"Message sent to {member.name}#{member.discriminator}")

                except discord.errors.Forbidden:

                    print(
                        f"Could not send message to {member.name}#{member.discriminator} (user has DMs disabled)")

                except Exception as e:

                    print(
                        f"An error occurred while sending message to {member.name}#{member.discriminator}: {e}")

@client.event
async def on_reaction_add(reaction, user):

    if reaction.message.content.startswith("**Présence :**"):

        # si la personne répond présent, on lui envoie le menu

        if str(reaction.emoji) == "✅":

            response = "présent"

            # récupération du vrai nom de la personne à partir de son nom discord afin de
            # lui envoyer son menu personnalisé en fonction des ses habitudes alimentaires
            # (stockées dans la base de données Odoo en fonction du vrai nom)

            name = hr_data.get_name_by_discord(str(user))

            # la fonction créé un dossier avec les images du menu personnalisé

            print(lunch_data.list_available_lunch(name))

            commande[name] = []

            await send_menu_with_images(user.dm_channel)

        elif str(reaction.emoji) == "❌":

            response = "pas présent"

            await user.send("Merci de votre réponse, bonne journée !")

        else:

            return

        print(f"{user.name} a répondu '{response}' au sondage.")

commande_traitee = False

@client.event
async def on_message(message):

    global offline

    global nombre_utilisateurs_attendus

    global commande_traitee

    if isinstance(message.channel, discord.DMChannel):

        user = message.author

        name = hr_data.get_name_by_discord(str(user))

        response = message.content

        if user == client.user:

            return

        if user != client.user:

            print(f"Réponse de {user.name}: {response}")

            verification_plat = verif_plat(response)

            if verification_plat:

                commande[name].append(response)

            else:

                await message.channel.send("Ce plat n'est pas disponible :( ")

        print(f"Commande : {commande}")

        # on attent un certain temps que tout le monde place sa commande

        await asyncio.sleep(10) # 30 secondes, variable que l'on peut changer en fonction du besoin

        if not commande_traitee:

            for noms, plats in commande.items():

                for plat in plats:

                    lunch_data.new_order(name, plat)

            commande_traitee = True

            await message.channel.send("La commande a été envoyée !")

            if len(commande) == nombre_utilisateurs_attendus:

                # await asyncio.sleep(10)  # Attendre une heure (3600 secondes)

                try:
                    await client.close()

                except RuntimeError as e:
                    if "Event loop is closed" in str(e):
                        pass  # Ignorer l'erreur "Event loop is closed"
                    else:
                        raise  # Relever toute autre erreur


client.run(TOKEN)