import authentication
import imap

imap_conn = authentication.authenticate()
imap_conn.select('INBOX')
imap.list_messages(imap_conn)
