import json
import os
import uuid
import requests

from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()

SUPABASE_URL: str = os.getenv("PAYMENT_SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("PAYMENT_SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase():
    return supabase


DB_SERVICE_URL: str = os.getenv("DB_SERVICE_URL")

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
    

def post(path: str, data: dict = {}):
    url = f"{DB_SERVICE_URL}/{path}"
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        raise ValueError(str(e))

def get(path: str, params: dict = {}):
    url = f"{DB_SERVICE_URL}/{path}"
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        raise ValueError(str(e))

def put(path: str, data: dict = {}):
    url = f"{DB_SERVICE_URL}/{path}"
    try:
        response = requests.put(url, json=data)
        return response.json()
    except Exception as e:
        raise ValueError(str(e))
