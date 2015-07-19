"""Handles IMAP operations for tMail, the terminal Gmail client"""
import os
import time
from os import path

from simplecrypt import decrypt, encrypt
import imaplib

from requests_oauthlib import OAuth2Session


CLIENT_ID = '47637480825-5d3ndp33q8m6eojt015p9th1q5cig3bm.apps.googleusercontent.com'
CLIENT_SECRET = 'xjFxdgVhJZjypUUoW7sC8R4Y'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
SCOPE = 'https://mail.google.com/'

SETTINGS_DIR = '.tmail'
SETTINGS_FILE = 'settings.txt'
REFRESH_KEY_FILE = '.refresh_key'
ACCESS_KEY_FILE = '.access_key'


def _generate_auth_string(user, token):
    """Generates the string to use when authenticating within IMAP"""
    return 'user=%s\1auth=Bearer %s\1\1' % (user, token)


def get_expiration():
    """Retrieves the access token expiration from the settings file"""
    with open(path.join(
        path.expanduser('~'),
        SETTINGS_DIR,
        SETTINGS_FILE)) as settings_file:
        for line in settings_file:
            if line.startswith('expiration'):
                tokens = line.split('=')
                return float(tokens[1])
        raise IOError('No expiration in settings')


def refresh_access_token():
    """Refreshes the access token"""
    with open(path.join(
        path.expanduser('~'),
        SETTINGS_DIR,
        ACCESS_KEY_FILE), 'rb') as key_file:
        refresh_token = key_file.read()
    refresh_token = decrypt(CLIENT_SECRET, refresh_token).decode('utf-8')
    google = OAuth2Session(client_id=CLIENT_ID)

    token = google.refresh_token(
        'https://accounts.google.com/o/oauth2/token',
        refresh_token=refresh_token,
        client_secret=CLIENT_SECRET,
        client_id=CLIENT_ID)

    return token['access_token'], token['expires_in']

def save_expiration(expiration):
    """Saves over any existing expiration in the settings file"""
    with open(
        path.join(path.expanduser('~'), SETTINGS_DIR, SETTINGS_FILE),
        'r+') as settings_file:
        lines = settings_file.readlines()
    with open(
        path.join(path.expanduser('~'), SETTINGS_DIR, SETTINGS_FILE),
        'w+') as settings_file:
        for line in lines:
            if not line.startswith('expiration'):
                settings_file.write(line)
    with open(
        path.join(path.expanduser('~'), SETTINGS_DIR, SETTINGS_FILE),
        'a+') as settings_file:
        settings_file.write('expiration=' + str(time.time() + expiration))


def get_access_token():
    """Retrieves the access token from the keys file"""
    try:
        expiration = get_expiration()
        assert expiration > time.time()
    except AssertionError:
        access_token, expiration = refresh_access_token()
        save_expiration(expiration)
        return access_token

    with open(path.join(
        path.expanduser('~'),
        SETTINGS_DIR,
        ACCESS_KEY_FILE), 'rb') as key_file:
        access_token = key_file.read()
    return decrypt(CLIENT_SECRET, access_token).decode('utf-8')


def get_username():
    """Retrieves the username from the settings file"""
    with open(path.join(
        path.expanduser('~'),
        SETTINGS_DIR,
        SETTINGS_FILE)) as settings_file:
        for line in settings_file:
            if line.startswith('username'):
                tokens = line.split('=')
                return tokens[1]
        raise IOError('No username in settings')

def oauth_process():
    """Goes through the OAuth2 process for Gmail"""
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    google = OAuth2Session(
        client_id=CLIENT_ID,
        scope=SCOPE,
        redirect_uri=REDIRECT_URI)
    authorization_url = google.authorization_url(
        'https://accounts.google.com/o/oauth2/auth')
    print('Please visit this url to authenticate: ')
    print(authorization_url)
    authorization_response = input('Please enter the authorization code: ')
    token = google.fetch_token(
        'https://accounts.google.com/o/oauth2/token',
        client_secret=CLIENT_SECRET,
        code=authorization_response)

    return token['refresh_token'], token['access_token'], float(token['expires_in'])


def save_username():
    username = input('Please enter your Gmail address: ')
    with open(
        path.join(path.expanduser('~'), SETTINGS_DIR, SETTINGS_FILE),
        'a+') as settings_file:
        settings_file.write('username=' + username + '\n')
    return username

def authenticate():
    """Authenticates the current user using OAuth2"""
    username = None

    try:
        access_token = get_access_token()
    except IOError:
        os.makedirs(path.join(path.expanduser('~'), SETTINGS_DIR), exist_ok=True)

        username = save_username()

        refresh_token, access_token, expiration = oauth_process()
        save_expiration(expiration)

        with open(
            path.join(path.expanduser('~'), SETTINGS_DIR, REFRESH_KEY_FILE),
            'wb+') as refresh_key_file:
            refresh_key_file.write(encrypt(CLIENT_SECRET, refresh_token))
        with open(
            path.join(path.expanduser('~'), SETTINGS_DIR, ACCESS_KEY_FILE),
            'wb+') as access_key_file:
            access_key_file.write(encrypt(CLIENT_SECRET, access_token))

    if username is None:
        try:
            username = get_username()
        except IOError:
            username = save_username()

    auth_string = _generate_auth_string(username, access_token)
    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_conn.authenticate('XOAUTH2', lambda x: auth_string.encode('ascii'))
    return imap_conn
