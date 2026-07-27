#!/bin/env python3

import unittest
from unittest.mock import patch, Mock
import sys
import csv
import json
from time import time
from datetime import datetime
from mastodon.return_types import Status, Context

sys.path.append('../')

import maint as main
import mastodon_listener
from mysql_store import MessageStore as MysqlStore

MASTODON_ID = 'test@example.com'
XMPP_JID = 'test@xmpp.org'
USERS_TEST_DB = 'users_test.db'
MESSAGES_TEST_DB = 'test_messages.db'

main.MYSQL_HOST = 'localhost'
main.MYSQL_PORT = '3306'
main.MYSQL_DATABASE = 'mastaj_test'
main.MYSQL_USERNAME = 'test'
main.MYSQL_PASSWORD = 'test'

main.USERS_DB = 'tests/users_test.db'

def loadPost(filename: str) -> dict:
    with open("tests/data/" + filename) as f:
        data = f.read()
        f.close()
    return json.loads(data)


class TestNewPost(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.message_store = MysqlStore(
            main.MYSQL_HOST, main.MYSQL_PORT, main.MYSQL_DATABASE, main.MYSQL_USERNAME, main.MYSQL_PASSWORD)
        cls.message_store.drop_database()
    
    def setUp(self):
        self.message_store = MysqlStore(
            main.MYSQL_HOST, main.MYSQL_PORT, main.MYSQL_DATABASE, main.MYSQL_USERNAME, main.MYSQL_PASSWORD)
        self.mastodon = Mock()
        listener = mastodon_listener.MastodonListener(MASTODON_ID, [XMPP_JID], None, None)
        mastodon_user = mastodon_listener.MastodonUser(MASTODON_ID, None)
        mastodon_user.listener = listener
        mastodon_user.mastodon = self.mastodon
        mastodon_user.jids = [XMPP_JID]
        main.mastodon_listeners[MASTODON_ID] = mastodon_user
    
    def tearDown(self):
        self.message_store.disconnect()

    def test_01_new_post(self):

        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post1 = loadPost("post0.json")

        with patch.object(main.mastodon_listeners[MASTODON_ID], "status_post", return_value=Status(**post1)):
            main.mastodon_post_status_process(XMPP_JID, in_reply_to_id=None, status="test message", visibility="public")

        mock_msg.send.assert_called_once()
        mock_msg.__setitem__.assert_called_once()
        mock_xmpp.make_message.assert_called_once_with(
            XMPP_JID,
            "test message",
            mfrom='3091105-0@megagate.lenovo.myhome',
            mtype='chat'
        )

    def test_02_new_post_as_reply(self):

        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post1 = loadPost("own_reply.json")

        with patch.object(main.mastodon_listeners[MASTODON_ID], "status_post", return_value=Status(**post1)):
            main.mastodon_post_status_process(XMPP_JID, in_reply_to_id='3091105-0', status="test message", visibility="public")

        mock_msg.send.assert_not_called()
        
        # message = self.message_store.get_messages_for_user_by_thread(MASTODON_ID, '3091106-0')
        # self.assertEqual(2, len(message))
