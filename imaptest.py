import oauth2 as oauth
from oauth2.clients import imap as imaplib
consumer = oauth.Consumer('', '')
token = oauth.Token('','')

url = 'https://mail.google.com/mail/b/storminnorton@gmail.com/imap/'

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.debug = 4

mail.authenticate(url, consumer, token)

mail.list()
