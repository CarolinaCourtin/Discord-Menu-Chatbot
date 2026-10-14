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


models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# recherche de l'ID du modèle hr.employee
model_id = models.execute_kw(db, uid, password, 'ir.model', 'search', [[('model', '=', 'hr.employee')]], {'limit': 1})
if model_id:
    model_id = model_id[0]

# création d'un nouveau field pour la table des rh (habitudes alimentaires)

def new_field_hr():

    if model_id:
        field_id = models.execute_kw(db, uid, password, 'ir.model.fields', 'create', [{
            'model_id': model_id,
            'name': 'x_habitudes_alimentaires',
            'field_description': 'Habitudes alimentaires',
            'ttype': 'char',
            'state': 'manual',
        }])

        print('ID du champ créé:', field_id)
    else:
        print("ID du modèle 'hr.employee' non trouvé.")

# affichage des fields de la table des employés
def show_field_json():

    print("Champs du modèle hr.employee :")
    employee_fields = models.execute_kw(db, uid, password, 'ir.model.fields', 'search_read',
                                        [[('model_id', '=', model_id)]], {'fields': ['name', 'field_description']})

    for field in employee_fields:
        print(field['name'], '-', field['field_description'])

    # Écrire les données dans un fichier JSON indenté
    output_file_path = 'employee_fields.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(employee_fields, output_file, indent=4)

    print(f"Les champs ont été enregistrés dans le fichier {output_file_path}")

# affichage des employés

def show_employees_json():
    employee_list = models.execute_kw(
        db,
        uid,
        password,
        'hr.employee',
        'search_read',
        [],
        {'fields': ['name', 'department_id', 'job_title', 'work_email', 'x_habitudes_alimentaires', "x_discord"]}
    )

    output_file_path = 'employee_list.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(employee_list, output_file, indent=4)

    print(f"Les champs ont été enregistrés dans le fichier {output_file_path}")

# ajouter les données au field des habitudes alimentaires pour les employés

def set_lunch_habits_employees():

    with open('employee_list.json', 'r') as json_file:

        data = json.load(json_file)

    ids = []
    for record in data:
        ids.append(record['id'])

    liste_regime = ["Vegan", "Vegetarien", "Sans gluten", "Sans lactose", "Sans porc"]

    for id in ids:
        regime = random.choice(liste_regime)

        habitudes_alimentaires_employes = models.execute_kw(db, uid, password, 'hr.employee', 'write',
                                                            [[id], {'x_habitudes_alimentaires': regime}])

    employee_list_updated = models.execute_kw(
        db,
        uid,
        password,
        'hr.employee',  # Nom du modèle
        'search_read',
        [],  # Aucun filtre supplémentaire
        {'fields': ['name', 'department_id', 'job_title', 'work_email', 'x_habitudes_alimentaires']}
    )

# enlever un field de la table des employés

def remove_field_hr():
    field_name_to_remove = 'x_habitudes_alimentaires'

    field_ids = models.execute_kw(db, uid, password, 'ir.model.fields', 'search', [[
        ('model', '=', 'hr.employee'),
        ('name', '=', field_name_to_remove),
    ]])

    if field_ids:
        models.execute_kw(db, uid, password, 'ir.model.fields', 'unlink', [field_ids])
        print("Champ supprimé avec succès.")
    else:
        print("Champ non trouvé dans le modèle 'hr.employee'.")

# ajout d'un field "discord" dans la table des employés pour avoir aussi le nom d'utilisateur discord des employés
def new_discord_field():

    if model_id:
        field_id = models.execute_kw(db, uid, password, 'ir.model.fields', 'create', [{
            'model_id': model_id,
            'name': 'x_discord',
            'field_description': 'Discord',
            'ttype': 'char',
            'state': 'manual',
        }])

        print('ID du champ créé:', field_id)
    else:
        print("ID du modèle 'hr.employee' non trouvé.")

# ajout d'un employé
def add_new_employee():
    new_employee_id = models.execute_kw(
        db,
        uid,
        password,
        'hr.employee',
        'create',
        [{
            'name': 'Carolina Courtin',
            'department_id': 1,
        }]
    )

    print("Nouvel employé ajouté avec l'ID:", new_employee_id)

# mise à jour du nom discord dans le nouveau field "discord"

def set_discord():
    models.execute_kw(
        db,
        uid,
        password,
        'hr.employee',
        'write',
        [[21], {'x_discord': "carolinac6758"}]
    )
    print(f"Nom d'utilisateur Discord ajouté pour l'employé avec l'ID 21")

# récupération du vrai nom de l'employé à partir de son discord (pour le bot)
# p.ex : Carolina Courtin = carolinac6758

def get_name_by_discord(discord_name):

    real_name = None

    with open('employee_list.json', 'r') as json_file:

        data = json.load(json_file)

        for employee_data in data:

            if employee_data['x_discord'] == discord_name:

                real_name = employee_data.get('name')

                break

    return real_name

# récupération de l'id d'un employé à partir de son nom

def get_id_by_name(name):

    id = None

    with open('employee_list.json', 'r') as json_file:

        data = json.load(json_file)

        for employee in data:

            if employee['name'] == name:

                id = employee.get('id')

                break

    return id

# print(get_id_by_name("Carolina Courtin"))
# print(get_name_by_discord("carolinac6758"))
