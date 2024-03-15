import firebase_admin
import os
from firebase_admin import credentials, db



Key_directory = os.path.dirname(os.path.abspath(__file__))
key_route = os.path.join(Key_directory,'KEY')
real_key = os.path.join(key_route,"game-db-e5ec7-firebase-adminsdk-t3bsc-7b75d9a005.json")

firebase_sdk = credentials.Certificate(real_key)
firebase_admin.initialize_app(firebase_sdk,{'databaseURL':'https://game-db-e5ec7-default-rtdb.firebaseio.com/'})

def Send_Data(Action,reference):
    ref = db.reference(reference)
    ref.set({'keyboard_actions':Action})

Reference = 'Game/Actions/-NszVxjdlbgwFwCzc33l'

