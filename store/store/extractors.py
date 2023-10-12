"""
File used for extracting sensitive data in the environment.
"""

import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def get_env_variables():
    """
    Extract the env.json to get sensitive data.
    """

    env_file = os.path.join(BASE_DIR, 'env.json')
    try:
        with open(env_file) as f:
            env_data = json.load(f)
    except FileNotFoundError:
        error_message = (
            f"""
            The env.json file '{env_file}' does not exist.
            Make sure to create it and put the required credentials.
            """
        )
        raise ImproperlyConfigured(error_message)
    except json.JSONDecodeError as e:
        raise ImproperlyConfigured(
            f"Error parsing the env.json file '{env_file}': {str(e)}")
    return env_data


def get_debug_settings():
    """
    Returns django DEBUG settings from env.json.
    """
    env_data = get_env_variables()
    return env_data['DEBUG']


def get_secret_key():
    """
    Returns django secret key from env.json.
    """
    env_data = get_env_variables()
    return env_data['SECRET_KEY']


def get_db_credentials():
    """
    Returns database credentials from env.json.
    """
    env_data = get_env_variables()
    db_credentials = {
        'NAME': env_data['DB_NAME'],
        'USER': env_data['DB_USER'],
        'PASSWORD': env_data['DB_PASSWORD'],
        'HOST': env_data['DB_HOST'],
        'PORT': env_data['DB_PORT'],
    }
    return db_credentials


def get_allowed_host():
    """
    Returns ALLOWED HOST from env.json.
    """
    env_data = get_env_variables()
    return env_data['ALLOWED_HOST']