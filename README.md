# Bot Discord de commande de repas connecté à Odoo

Un chatbot Discord qui permet aux employés d'une entreprise de commander leur repas de midi directement dans Discord. Les commandes sont enregistrées automatiquement dans le module **Lunch** de l'ERP **Odoo**. Le module Lunch d'Odoo ne tient pas compte des régimes alimentaires : chaque employé doit chercher lui-même les plats qui lui conviennent. Ce projet ajoute donc à Odoo le régime alimentaire des employés et des plats (végétarien, vegan, sans porc, sans gluten, sans lactose). Le bot peut ainsi envoyer à chacun un **menu personnalisé**. Ce projet a été réalisé dans le cadre du cours Systèmes d'Information d'Entreprise à l'Université de Genève lors du semestre de printemps 2024. 

## Fonctionnement

1. Le bot envoie en message privé un **formulaire de présence** à tous les membres en ligne du serveur.
2. Quand un employé répond présent (réaction ✅), le bot récupère son régime alimentaire dans Odoo. Il lui envoie ensuite un **menu PDF** avec les plats compatibles : photo, description, prix et régime.
3. L'employé écrit au bot le nom du ou des plats choisis. Le bot vérifie que chaque plat existe.
4. Une fois le délai de commande passé, le bot crée les commandes dans le module Lunch d'Odoo, qui les transmet au fournisseur.

| Processus de commande avec le bot (BPMN) | Exemple de menu envoyé |
|---|---|
| ![BPMN](docs/bpmn-to-be.png) | ![Menu](docs/menu-example.png) |

## Technologies

- **Python** avec [discord.py](https://discordpy.readthedocs.io/) pour le bot
- L'**API externe d'Odoo** (XML-RPC) pour lire et écrire dans les modules Employés et Lunch, avec les méthodes `search_read`, `create` et `write`. Elle sert aussi à créer de nouveaux champs : régime alimentaire et pseudo Discord.
- **fpdf2** pour générer les menus en PDF
- **BPMN** pour modéliser le processus avant et après l'intégration

## Structure

```
├── discord_lunch_bot_without_close.py  # Bot (version principale, reste en ligne)
├── discord_lunch_bot_with_close.py     # Variante qui se déconnecte une fois les commandes passées (expérimentale)
├── lunch_data.py    # Fonctions Odoo : plats, régimes alimentaires, création des commandes
├── hr_data.py       # Fonctions Odoo : employés, habitudes alimentaires, pseudo Discord
├── users_data.py    # Fonctions Odoo : utilisateurs
├── config.py        # Lecture de la configuration (.env)
├── *.json           # Copies locales des données Odoo (employés, plats, utilisateurs…)
└── images/          # Images des plats du menu en cours
```

Au lancement, le bot envoie le formulaire de présence aux membres en ligne. L'employé ajoute la réaction ✅ au message pour recevoir son menu. Il envoie ensuite le nom exact d'un plat (par exemple `Pizza Italiana`). Après le délai d'attente (30 secondes dans le code, modifiable), la commande est créée dans Odoo.
