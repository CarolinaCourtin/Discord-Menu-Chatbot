import base64
import os
import xmlrpc.client
import json
import random

from config import ODOO_URL as url, ODOO_DB as db, ODOO_USERNAME as username, ODOO_PASSWORD as password

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print(common.version())

uid = common.authenticate(db, username, password, {})

if uid:
    print("Authentication success")
else:
    print("Authentication failed")

# check if we can read the res.partner model

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# example_model = models.execute_kw(db, uid, password, 'res.partner', 'check_access_rights',
# ['read'], {'raise_exception': False})

# ID du modèle lunch

model_lunch_id = models.execute_kw(
    db,
    uid,
    password,
    'ir.model',
    'search',
    [[('model', '=', 'lunch.product')]],
    {'limit': 1}
)

if model_lunch_id:
    model_lunch_id = model_lunch_id[0]

# récupération des fields de la table lunch
def show_field_json():

    lunch_fields = models.execute_kw(
        db,
        uid,
        password,
        'lunch.order',
        'fields_get',
        [],
        {'attributes': ['string', 'type']}
    )

    output_file_path = 'lunch_fields.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(lunch_fields, output_file, indent=4)

    print(f"Les champs ont été enregistrés dans le fichier {output_file_path}")

# ajout d'un field dans la table lunch (habitudes alimentaires)
def new_field_lunch():

    if model_lunch_id:
        field_id = models.execute_kw(
            db,
            uid,
            password,
            'ir.model.fields',
            'create',
            [{
                'model_id': model_lunch_id,
                'name': 'x_regime_alimentaire',
                'field_description': 'Régime alimentaire',
                'ttype': 'char',
                'state': 'manual',
            }]
        )

        print("Champ créé avec l'ID :", field_id)
    else:
        print("Le modèle 'lunch.product' n'a pas été trouvé.")

# affichage des fields de la table des produits dans lunch
def show_products_fields():
    product_fields = models.execute_kw(
        db,
        uid,
        password,
        'ir.model.fields',
        'search_read',
        [[('model_id.model', '=', 'lunch.product')]],
        {'fields': ['name', 'field_description']}
    )

    for field in product_fields:
        print(field['name'], '-', field.get('field_description', 'Description non disponible'))

    output_file_path = 'product_fields.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(product_fields, output_file, indent=4)

    print(f"Les informations sur les champs ont été enregistrées dans le fichier {output_file_path}")

# affichage des produits

def show_lunch_info():
    lunch_list = models.execute_kw(
        db,
        uid,
        password,
        'lunch.product',
        'search_read',
        [],
        {'fields': ['name', 'price', 'x_regime_alimentaire', 'description']}
    )

    output_file_path = 'products.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(lunch_list, output_file, indent=4)

    print(f"Les champs ont été enregistrés dans le fichier {output_file_path}")


# ajouter des données dans le nouveau field regime alimentaire des produits

def update_lunch_diet():
    with open('products.json', 'r') as json_file:
        data = json.load(json_file)

    # boucle pour récupérer tous les ID des lunchs et les modifier
    ids = []
    for record in data:
        ids.append(record['id'])

    liste_regime = ["Vegan", "Vegetarien", "Sans gluten", "Sans lactose", "Sans porc"]

    for id in ids:
        regime = random.choice(liste_regime)

        habitudes_alimentaires_employes = models.execute_kw(db,
                                                            uid,
                                                            password,
                                                            'lunch.product',
                                                            'write',
                                                            [[id],
                                                             {'x_regime_alimentaire': regime}])

    products_updated = models.execute_kw(
        db,
        uid,
        password,
        'lunch.product',
        'search_read',
        [],
        {'fields': ['name', 'price', 'x_regime_alimentaire']}
    )

    show_lunch_info()

# enlever un field du module lunch.order
def remove_field_lunch():
    field_name_to_remove = 'x_regime_alimentaire'

    field_ids = models.execute_kw(db, uid, password, 'ir.model.fields', 'search', [[
        ('model', '=', 'lunch.order'),
        ('name', '=', field_name_to_remove),
    ]])

    if field_ids:
        models.execute_kw(db, uid, password, 'ir.model.fields', 'unlink', [field_ids])
        print("Champ supprimé avec succès.")
    else:
        print("Champ non trouvé dans le modèle 'lunch.product'.")

def clear_folder(folder):
    # Parcours de tous les fichiers dans le dossier
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            # Suppression de chaque fichier
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Erreur lors de la suppression de {file_path}: {e}")

# creation du menu en fonction des habitudes alimentaires des employés
def list_available_lunch(employee_name):

    lunch_name_list = []
    prix_list = []

    regime_alimentaire = None

    with open('employee_list.json', 'r') as json_file:

        data = json.load(json_file)

        for employee_data in data:

            if employee_data['name'] == employee_name:

                regime_alimentaire = employee_data.get('x_habitudes_alimentaires')

                print(f"Régime alimentaire de {employee_name} : {regime_alimentaire}")

                break

    lunches = models.execute_kw(
        db,
        uid,
        password,
        'lunch.product',
        'search_read',
        [[('x_regime_alimentaire', '=', regime_alimentaire)]],
        {'fields': ['name', 'image_1920', 'price']}
    )

    image_folder = "images"

    clear_folder(image_folder)

    for lunch in lunches:
        lunch_name = lunch['name']
        image_base64 = lunch['image_1920']
        prix = lunch['price']

        lunch_name_list.append(lunch_name)
        prix_list.append(prix)

        output_file_path = os.path.join(image_folder, f"{lunch_name}.png")

        with open(output_file_path, 'wb') as f:

            f.write(base64.b64decode(image_base64))

        print(f"Nom du lunch: {lunch_name}, Prix: {prix}")

    return lunch_name_list, prix_list

# affichage des commandes
def show_orders():

    orders = models.execute_kw(
        db,
        uid,
        password,
        'lunch.order',
        'search_read',
        [[]],
        {'fields': ['name', 'date', 'user_id', 'quantity']}
    )

    output_file_path = "orders.json"

    with open(output_file_path, 'w') as output_file:

        json.dump(orders, output_file, indent=4)

    print(f"Les champs ont été enregistrés dans le fichier {output_file_path}")

# création d'une nouvelle commande

def new_order(name, food):

    product_id = None

    name_id = None

    with open("products.json", 'r') as f:

        data = json.load(f)

        for product in data:

            if product['name'] == food:

                product_id = product.get('id')

    with open("utilisateurs.json", 'r') as u:

        data = json.load(u)

        for user in data:

            if user['name'] == name:
                name_id = user.get('id')

    id = models.execute_kw(db,
                           uid,
                           password,
                           'lunch.order',
                           'create',
                               [{'name':food,
                                 'user_id': name_id,
                                 "product_id": product_id}])




