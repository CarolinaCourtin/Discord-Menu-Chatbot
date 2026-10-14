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

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

def get_users():

    users = models.execute_kw(
        db,
        uid,
        password,
        'res.users',
        'search_read',
        [[]],
        {'fields': ['id', 'name', 'login']}
    )

    with open('utilisateurs.json', 'w') as f:

        json.dump(users, f, indent=4)


get_users()