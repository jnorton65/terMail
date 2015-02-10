#! /usr/bin/python
"""This python app effectively creates a terminal version of gmail. It will be
able to compose new messages, list various messages, reply to them, and move
them within the gmail system."""

import argparse
import os
import tempfile

from message import Message
from subprocess import call


def main():
    """The Gmail terminal app main function"""
    parser = setup_parser()
    args = parser.parse_args()

    if args.mode is None or args.mode == 'list':
        pass
    elif args.mode == 'compose':
        compose(parse_compose(args))
    elif args.mode == 'reply':
        pass
    elif args.mode == 'forward':
        pass
    elif args.mode == 'delete':
        pass


def setup_parser():
    """Set up the argument parser to correctly match terminal arguments"""
    parser = argparse.ArgumentParser(description='CLI Gmail App')
    subparsers = parser.add_subparsers(
        title='subcommands',
        description='Valid Gmail Commands',
        help='additional help',
        dest='mode')
    subparsers = setup_compose_parser(subparsers)
    subparsers = setup_list_parser(subparsers)
    return parser


def setup_compose_parser(subparsers):
    """Set up the argument parser to correctly match composition arguments"""
    parser_compose = subparsers.add_parser('compose')
    parser_compose.add_argument(
        '-d',
        '--draft',
        default=False,
        action='store_true',
        help='Store as a draft instead of sending right away')
    parser_compose.add_argument(
        '-s',
        '--subject',
        help='Use this as the subject of a new message')
    parser_compose.add_argument(
        '-t',
        '-to',
        dest='to',
        help='A list of comma separated email addresses to send the message to')
    parser_compose.add_argument(
        '--cc',
        help='A list of comma separated email addresses to cc the message to')
    parser_compose.add_argument(
        '--bcc',
        help='A list of comma separated email addresses to bcc the message to')
    parser_compose.add_argument(
        '--body',
        help='The body of the message')
    parser_compose.add_argument(
        '--from',
        dest='send_from',
        help='The email to send the message from, if not the default')
    parser_compose.add_argument(
        '--skip',
        default=False,
        action='store_true',
        help='Skip opening the editor, send with options provided')
    return subparsers


def setup_list_parser(subparsers):
    """Set up the argument parser to correctly match listing arguments"""
    return subparsers


def parse_compose(args):
    """Parse the arguments for the compose command and put them into a Message"""
    message = Message()
    if args.draft is True:
        message.is_draft = True
    if args.subject is not None:
        message.subject = args.subject
    if args.to is not None:
        message.send_to = args.to
    if args.cc is not None:
        message.send_cc = args.cc
    if args.bcc is not None:
        message.send_bcc = args.bcc
    if args.body is not None:
        message.body = args.body
    if args.send_from is not None:
        message.send_from = args.send_from
    if args.skip is True:
        message.skip = True
    return message


def compose(message):
    """Set up the message composition, then get the input"""
    editor = os.environ.get('EDITOR', 'vim')
    subject_str = 'SUBJECT: ' + message.subject + '\n'
    to_str = 'TO: ' + message.send_to + '\n'
    cc_str = 'CC: ' + message.send_cc + '\n'
    bcc_str = 'BCC: ' + message.send_bcc + '\n'
    from_str = 'FROM: ' + message.send_from + '\n'
    body_str = 'BODY: \n\n' + message.body

    with tempfile.NamedTemporaryFile(suffix=".tmp") as new_msg:
        new_msg.write(bytes(subject_str, 'UTF-8'))
        new_msg.write(bytes(to_str, 'UTF-8'))
        new_msg.write(bytes(cc_str, 'UTF-8'))
        new_msg.write(bytes(bcc_str, 'UTF-8'))
        new_msg.write(bytes(from_str, 'UTF-8'))
        new_msg.write(bytes(body_str, 'UTF-8'))
        new_msg.flush()
        if message.skip is False:
            call([editor, new_msg.name])
        new_msg.seek(0)
        separate_new_message(new_msg.read().decode('UTF-8').split('\n'))


def separate_new_message(lines):
    """Separates text lines into a message object"""
    i = 1
    new_message = {}
    area = ""
    areas = ['SUBJECT:', 'TO:', 'CC:', 'BCC:', 'FROM:', 'BODY:']
    for line in lines:
        if len(area) == 0:
            area = line
        else:
            if i < len(areas) and line.startswith(areas[i]):
                area = area.replace(areas[i-1], '', 1)
                new_message[areas[i-1]] = area
                area = line
                i += 1
            else:
                area += line
    area = area.replace(areas[i-1], '', 1)
    new_message[areas[i-1]] = area

    for area in new_message.values():
        print(area)

if __name__ == "__main__":
    main()
