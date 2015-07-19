import datetime

import email

import imap


def iterate_messages(M, messages):
    for num in reversed(messages):
        rv, data = M.fetch(num, '(BODY.PEEK[HEADER])')
        if rv != 'OK':
            print('ERROR getting message', num)
            return
        msg = email.message_from_string(data[0][1].decode('utf-8'))
        print('%s.\n%s' % (num.decode('utf-8'), msg['Subject']))
        print('From: %s' % msg['From'])
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            print('Date:', \
            local_date.strftime('%a, %d %b %Y %H:%M:%S'))
        print('\n')


def list_messages(M):
    print('Unread Messages:')
    rv, data = M.search(None, '(UNSEEN)')
    iterate_messages(M, data[0].split())

    print('Read Messages:')
    rv, data = M.search(None, '(SEEN)')
    iterate_messages(M, data[0].split())
