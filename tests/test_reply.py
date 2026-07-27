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


class TestNotification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.message_store = MysqlStore(
            main.MYSQL_HOST, main.MYSQL_PORT, main.MYSQL_DATABASE, main.MYSQL_USERNAME, main.MYSQL_PASSWORD)
        cls.message_store.drop_database()
        # cls.message_store = MysqlStore(
        #     main.MYSQL_HOST, main.MYSQL_PORT, main.MYSQL_DATABASE, main.MYSQL_USERNAME, main.MYSQL_PASSWORD)
    
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

    def test_01_reply_to_unknown_message(self):

        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post1 = loadPost("post1.json")
        post1['created_at'] = datetime.fromisoformat(post1['created_at'].replace("Z", "+00:00"))

        # self.mastodon.status.return_value = Status(**post0)
        # self.mastodon.status_context.return_value = Context(**post0_context)
        
        # Got update
        listener = main.mastodon_listeners[MASTODON_ID].listener
        m = listener.process_update(post1)
        main._mastodon_process_reply_process(MASTODON_ID, m, 'notification')
        
        mock_xmpp.make_message.assert_called_once_with(
            XMPP_JID,
            "@https://mastodon.world/ap/users/115722092263279862:\n@test, @test Сколько раз наблюдал такое на форумах (в основном технических): пойдет тенденция в одну сторону — все начинают поддакивать. Через год почему-то качнется в другую — и те же самые участники начинают неистово защищать противоположную точку зрения.",
            mfrom='home@megagate.lenovo.myhome',
            mtype='chat'
        )

        mock_msg.send.assert_called_once()
        mock_msg.__setitem__.assert_called_once()

        message = self.message_store.get_messages_for_user(MASTODON_ID)
        self.assertEqual(['3091105-1'], message)

        message = self.message_store.get_messages_for_user_by_thread(MASTODON_ID, '3091105-0')
        self.assertEqual(0, len(message))

        self.message_store.drop_database()

    def test_02_reply_to_my_known_message(self):

        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        toot = loadPost("post0.json")
        toot['created_at'] = datetime.fromisoformat(toot['created_at'].replace("Z", "+00:00"))

        post1 = loadPost("post1.json")
        post1['created_at'] = datetime.fromisoformat(post1['created_at'].replace("Z", "+00:00"))

        self.message_store.add_message(
            toot['content'],
            toot['url'],
            '@' + MASTODON_ID,
            [],
            'public',
            toot['id'],
            MASTODON_ID,
            toot['created_at'],
            int(time() * 1000),
            toot['id']
        )

        # self.mastodon.status.return_value = Status(**post0)
        # self.mastodon.status_context.return_value = Context(**post0_context)
        
        # Got update
        listener = main.mastodon_listeners[MASTODON_ID].listener
        m = listener.process_update(post1)
        main._mastodon_process_reply_process(MASTODON_ID, m, 'notification')
        
        mock_xmpp.make_message.assert_called_once_with(
            XMPP_JID,
            "@https://mastodon.world/ap/users/115722092263279862:\n@test, @test Сколько раз наблюдал такое на форумах (в основном технических): пойдет тенденция в одну сторону — все начинают поддакивать. Через год почему-то качнется в другую — и те же самые участники начинают неистово защищать противоположную точку зрения.",
            mfrom='3091105-0@megagate.lenovo.myhome',
            mtype='chat'
        )

        mock_msg.send.assert_called_once()
        mock_msg.__setitem__.assert_called_once()

        message = self.message_store.get_messages_for_user(MASTODON_ID)
        self.assertEqual([], message)

        message = self.message_store.get_messages_for_user_by_thread(MASTODON_ID, '3091105-0')
        self.assertEqual(2, len(message))

    def test_03_reply_to_known_message(self):
        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post1 = loadPost("post1.json")
        post1_context = loadPost("post1_context.json")
        post2 = loadPost("post2.json")
        post2['created_at'] = datetime.fromisoformat(post2['created_at'].replace("Z", "+00:00"))

        self.mastodon.status.return_value = Status(**post1)
        self.mastodon.status_context.return_value = Context(**post1_context)

        # Got update
        listener = main.mastodon_listeners[MASTODON_ID].listener
        m = listener.process_update(post2)
        main._mastodon_process_reply_process(MASTODON_ID, m, 'notification')
        
        mock_xmpp.make_message.assert_called_once_with(
            XMPP_JID,
            "@https://libranet.de/profile/wthinker:\n@Anonymous, @test @mamohin Это потому, что мир состоит в основном из право-левацких уклонистов. )",
            mfrom='3091105-0@megagate.lenovo.myhome',
            mtype='chat'
        )

        mock_msg.send.assert_called_once()
        mock_msg.__setitem__.assert_called_once()

        message = self.message_store.get_messages_for_user(MASTODON_ID)
        self.assertEqual([], message)

        message = self.message_store.get_messages_for_user_by_thread(MASTODON_ID, '3091105-0')
        self.assertEqual(3, len(message))

        self.message_store.drop_database()

    def test_04_update(self):
        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post0 = loadPost("update.json")
        post0['created_at'] = datetime.fromisoformat(post0['created_at'].replace("Z", "+00:00"))

        # Got update
        listener = main.mastodon_listeners[MASTODON_ID].listener
        m = listener.process_update(post0)
        main._mastodon_process_reply_process(MASTODON_ID, m, 'update')
        
        mock_xmpp.make_message.assert_called_once_with(
            XMPP_JID,
            "@test2:\ntest message",
            mfrom='home@megagate.lenovo.myhome',
            mtype='chat'
        )

        mock_msg.send.assert_called_once()
        mock_msg.__setitem__.assert_called_once()

        message = self.message_store.get_messages_for_user(MASTODON_ID)
        self.assertEqual(['3091106-0'], message)

        message = self.message_store.get_messages_for_user_by_thread(MASTODON_ID, '3091106-0')
        self.assertEqual(0, len(message))

        self.message_store.drop_database()

    def test_05_own_update_other(self):
        """Get update with our own post we posted from other client (web, etc.). Message isn't in DB"""
        # Should be sent to xmpp as start of new thread

        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post0 = loadPost("post0.json")
        post0['created_at'] = datetime.fromisoformat(post0['created_at'].replace("Z", "+00:00"))

        # Got update
        listener = main.mastodon_listeners[MASTODON_ID].listener
        m = listener.process_update(post0)
        main._mastodon_process_reply_process(MASTODON_ID, m, 'update')

        mock_xmpp.make_message.assert_called_once_with(
            XMPP_JID,
            "@test: start post",
            mfrom='3091105-0@megagate.lenovo.myhome',
            mtype='chat'
        )

        message = self.message_store.get_messages_for_user_by_thread(MASTODON_ID, '3091105-0')
        self.assertEqual(1, len(message))

    def test_06_own_update(self):
        """Get update with our own post. It's already in DB"""
        # Should be ignored

        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post0 = loadPost("post0.json")
        post0['created_at'] = datetime.fromisoformat(post0['created_at'].replace("Z", "+00:00"))

        # Got update
        listener = main.mastodon_listeners[MASTODON_ID].listener
        m = listener.process_update(post0)
        main._mastodon_process_reply_process(MASTODON_ID, m, 'update')
        
        mock_xmpp.make_message.assert_not_called()

    def test_07_own_update_as_reply(self):
        """Get update with our own reply from other client (web, etc.). Message isn't in DB"""
        # Should be sent to xmpp as part of thread

        mock_xmpp = Mock()
        mock_msg = Mock()
        mock_msg.__setitem__ = Mock()
        mock_xmpp.make_message.return_value = mock_msg

        main.XMPP = mock_xmpp

        post0 = loadPost("own_reply.json")
        post0['created_at'] = datetime.fromisoformat(post0['created_at'].replace("Z", "+00:00"))

        # Got update
        listener = main.mastodon_listeners[MASTODON_ID].listener
        m = listener.process_update(post0)
        main._mastodon_process_reply_process(MASTODON_ID, m, 'update')
        
        mock_xmpp.make_message.assert_called_once_with(
            XMPP_JID,
            "@test: my own reply to somebody",
            mfrom='3091105-0@megagate.lenovo.myhome',
            mtype='chat'
        )

        message = self.message_store.get_messages_for_user_by_thread(MASTODON_ID, '3091105-0')
        self.assertEqual(['3091105-1', '3091105-0'], message)
