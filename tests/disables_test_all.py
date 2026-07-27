#!/usr/bin/env python3

import unittest
import sys
import re

# sys.path.append('./venv/lib/python3.7/site-packages')
sys.path.append('../venv/lib/python3.9/site-packages')
sys.path.append('../')
sys.path.append('.')
sys.path.append('./venv/lib/python3.9/site-packages')
import threading
import mastodon_listener
from sqlite_store import MessageStore
from mysql_store import MessageStore as MysqlStore
import gxmpp
from queue import Empty, Queue
import json
import db
import time
import csv
from datetime import datetime, timezone
from shutil import copyfile
import maint as main
from mastodon import StreamListener


UPDATES_FILE = 'mastodon_update.json'
NOTIFICATIONS_FILE = 'mastodon_notification.json'

UPDATES_RSULT_FILE = 'mastodon_updates.txt'
NOTICICATIONS_RESULT_FILE = 'mastodon_notifications.txt'

MASTODON_ID='shura@mastodon.social'
USERS_TEST_DB='users_test.db'
MESSAGES_TEST_DB='test_messages.db'

MYSQL_HOST='localhost'
MYSQL_PORT='3306'
MYSQL_DATABASE='mastaj_test'
MYSQL_USERNAME='test'
MYSQL_PASSWORD='test'

update_queue=Queue()

def test_messages(self, dbtype='sqlite'):
        tmp_db=MESSAGES_TEST_DB+'.bak'
        copyfile(MESSAGES_TEST_DB, tmp_db)
        if dbtype == 'sqlite':
            message_store=MessageStore(tmp_db)
        else:
            message_store=MysqlStore(MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE,
             MYSQL_USERNAME, MYSQL_PASSWORD)
        # mentions=set(['@test@mastodon.social'])
        # _id=104032314153599025
        # message_store.update_mentions(_id, mentions)
        # toot=message_store.get_message_by_id(_id)
        # sample=set(['@test@mastodon.social','@groosha@mastodon.ml'])
        # self.assertEqual(set(toot['mentions'].split(' ')),sample)
        # mentions=set(['@test@mastodon.social', '@test2@mastodon.social'])
        # message_store.update_mentions(_id, mentions)
        # toot=message_store.get_message_by_id(_id)
        # sample.update(['@test2@mastodon.social'])
        # self.assertEqual(set(toot['mentions'].split(' ')),sample)
        # toot['mentions']=toot['mentions'].split(' ')
        # toot['author']=toot['mentions'][0]
        # toot['date'] = datetime.fromisoformat(toot['date'])
        # print(*toot)
        # res = message_store.add_message(**toot)
        # self.assertEqual(res, None)
        # toot['mid']='test@test.tld'
        # res = message_store.add_message(**toot)
        # self.assertNotEqual(res, None)
        
        search_for='''"Linux". А то юзаю как чайник.'''
        toot=message_store.find_message(search_for, 'shura@mastodon.social')
        # print(toot)
        self.assertEqual(toot['id'],'104032564439980906')
        search_for='''@sptnkmmnt@mastodon.ml:
Когда-то очень давно, я записывал концерт Spititual Front на айпад.  
В смысле, стоял в зале и снимал.  
Сейчас понимаю, как тупо я выглядел.  
И меня мучает вопрос:
Интересно, а как музыкантов не бесит, что вместо того, чтобы наслаждаться музыкой, текстами, там... шоу, в конце концов, народ утыкается в смарты и просто "ксерокопирует" форму без содержания?'''
        toot=message_store.find_message(search_for, 'shura@mastodon.social')
        self.assertEqual(toot['id'],'104032809534204360')
        
        search_for='''@Vladimir_Vladimirovich:
Судно "Академик Черский", способное достроить "Северный поток-2", которое по данным независимых СМИ шло в Находку, внезапно оказалось у берегов Дании. Наверное решили идти в Находку Северным морским путём.'''
        toot=message_store.find_message(search_for, 'shura@mastodon.social')
        self.assertEqual(toot,None)
        
        search_for='''С одной стороны я достаточно долго не любил тот же Озон и ко за то, что они были членами АКИТ и лоббировали снижение беспошлинных лимитов, и прочее. С другой стороны они в это же время выстроили классную логистику с оглядкой на Amazon и это реально УДОБНО и просто.'''
        toot=message_store.find_message(search_for, 'L29Ah@qoto.org')
        self.assertEqual(toot['id'],'105237775817950579')
        
        search_for='''С одной стороны я достаточно долго не любил тот же Озон и ко за то, что они были членами АКИТ и лоббировали снижение беспошлинных лимитов, и прочее. С другой стороны они в это же время выстроили классную логистику с оглядкой на Amazon и это реально УДОБНО и просто.'''
        toot=message_store.find_message(search_for, 'shura@mastodon.social')
        self.assertEqual(toot['id'],'105237775810751372')

class TestAll(unittest.TestCase):
    
    def _p_update(self):
        message_store=self.message_store
        message = self.update_queue.get(block=False)
        #print(message)
        _m=message['status']
        print("mid:",message['mid'])
        print("mentions:", _m.mentions)
        answer_to_known_message=0
        if _m.in_reply_to_id:
            # thread=message['m'].get_thread(_m.id)
            # first_message=thread[0]
            # stored_message=message_store.get_message_by_id(first_message.id)
            # if stored_message:
            #     message_store.update_mentions(first_message.id,_m.mentions)
            #     mentions_str=stored_message['mentions']
            #     mentions=set(mentions_str.split(' '))
            #     if message['mid'] in mentions:
            #         answer_to_known_message=1
            pass
        else:
            #autobost processing
            try:
                print("autoboost processing")
                for j in message['m'].jids:
                    print("for "+str(j))
                    # l=users_db.getAutoboostByJid(j)
                    # print("autoboost names:\n"+str(l))
                    # print("post from "+str(_m.from_mid))
                    # if _m.from_mid.lower() in l:
                    #     print("got reblog")
                        # mastodon=mastodon_listeners.get(message['mid'])
                        # if mastodon:
                        #     mastodon.status_reblog(_m.id)
            except Exception as e:
                print(str(e))
        if answer_to_known_message:
            for j in message['m'].jids:
                # msg = XMPP.make_message(j,
                #                 _m.text,
                #                 mfrom=str(first_message.id)+'@'+HOST,
                #                 mtype='chat')
                # msg.send()
                pass
        else:
            if '@'+message['mid'] not in _m.mentions:
                print("Before DB adding:")
                print(message)
                print(_m.to_dict())
                message_store.add_message(
                    _m.text,
                    _m.url,
                    _m.from_mid,
                    _m.mentions,
                    _m.visibility,
                    _m.id,
                    message['mid'],
                    _m.date,
                    _m.receive_time
                )
                if _m.in_reply_to_id:
                    for j in message['m'].jids:
                        # check if user has disabled replies receiving
                        # u=users_db.get_user_by_jid(j)
                        # if u and u['receive_replies']=='1':
                            # msg = XMPP.make_message(j,
                            #                     _m.text,
                            #                     mfrom='home@'+HOST,
                            #                     mtype='chat')
                            # msg.send()
                        pass
                else:
                    for j in message['m'].jids:
                        # msg = XMPP.make_message(j,
                        #                     _m.text,
                        #                     mfrom='home@'+HOST,
                        #                     mtype='chat')
                        # msg.send()
                        pass
            else:
                print("recipient is in mentions. Ignored")
                print("from_id=",_m.from_mid)
                print("to:", message['mid'])
                print("in reply to ",_m.in_reply_to_id)
                if ( not _m.in_reply_to_id ) and _m.from_mid == message['mid']:
                    print("Our own new message. Putting it in home chat")
                    message_store.add_message(
                        _m.text,
                        _m.url,
                        _m.from_mid,
                        _m.mentions,
                        _m.visibility,
                        _m.id,
                        message['mid'],
                        _m.date,
                        _m.receive_time
                    )
                    for j in message['m'].jids:
                        # msg = XMPP.make_message(j,
                        #                     _m.text,
                        #                     mfrom='home@'+HOST,
                        #                     mtype='chat')
                        # msg.send()
                        pass
                # No need to send message. We will receive a duplicate via notification
                #pass
    
    #def test_messages_sqlite(self):
    #    return test_messages(self)
    
    def test_messages_mysql(self):
        test_messages(self, 'mysql')
    
    def disable_test_update(self):
        """
        Test for mastodon update processing
        """
        self.maxDiff=None
        with open(UPDATES_FILE) as f:
            data=f.read()
        f.close()
        j = json.loads(data)
        q = Queue()
        self.update_queue=Queue()
        tmp_db=MESSAGES_TEST_DB+'.bak'
        copyfile(MESSAGES_TEST_DB, tmp_db)
        self.message_store=MessageStore(tmp_db)
        m=mastodon_listener.MastodonListener(MASTODON_ID)
        m.jids={'shura0@jabber.ru'}
        if type(j) is list:
            for i in j:
                r=m.process_update(i)
                #self.update_queue.put(i)
                self.update_queue.put({'mid': MASTODON_ID, 'status': r, 'm':m})
                q.put(r)
        else:
            r=m.process_update(j)
            self.update_queue.put({'mid': MASTODON_ID, 'status': r, 'm':m})
            q.put(r)
        

        with open(UPDATES_RSULT_FILE) as f:
            data=f.read()
        ju=json.loads(data)
        f.close()
        ll=[]
        while not q.empty():
            m=q.get()
            u=ju.pop(0)

            em=mastodon_listener.EncodedMessage()
            em.text=u['text']
            em.id=u['id']
            em.url=u['url']
            em.date=u['date']
            em.in_reply_to_id=u.get('in_reply_to_id')
            em.visibility=u['visibility']
            em.add_mentions(u['mentions'])
            em.from_mid=u['from_mid']
            ment=em.mentions
            mm=m.to_dict()
            mm['date'] = str(mm['date'])
            self.assertEqual(mm, em.to_dict())
            # self._p_update()
            # text=u['text']
            # print("u=")
            # print(u)
            # res=self.message_store.find_message(text, MASTODON_ID)
            # self.assertEqual(u['text'],res['message'])
        
    def disable_test_notification(self):
        with open(NOTIFICATIONS_FILE) as f:
            data=f.read()
        f.close()
        j = json.loads(data)
        q = Queue()
        m=mastodon_listener.MastodonListener(MASTODON_ID)
        if type(j) is list:
            for i in j:
                m.on_notification(i)
        else:
            m.on_notification(j)

        with open(NOTICICATIONS_RESULT_FILE) as f:
            u=f.read()
        ju=json.loads(u)
        f.close()
        while not q.empty():
            m=q.get()
            u=ju.pop(0)
            em=mastodon_listener.EncodedMessage()
            em.text=u['text']
            em.id=u['id']
            em.url=u['url']
            em.visibility=u['visibility']
            em.add_mentions(u['mentions'])
            self.assertEqual(m['status'].to_dict(), em.to_dict())

    def disable_test_users(self):
        tmp_db=USERS_TEST_DB+'.bak'
        copyfile(USERS_TEST_DB, tmp_db)
        database = db.Db(tmp_db)
        users=database.get_users()
        self.assertEqual(len(users),3)
        mu=main.get_uniq_mids(users)
        emu={
            'shura@mastodon.social': {
                'jids': ['admin@lenovo.myhome', 'admin@home.myhome'],
                'token': '53c6c387a730b42586042ceb69e2e6581ca4602ba406f758cf71019ff8ce9b71',
                'receive_replies': '1'},
            'onemore@masto.test': {
                'jids': ['user2@home.myhome'],
                'token': '111',
                'receive_replies': '1'}
            }
        self.assertEqual(mu,emu)
        
        database.add_user('test@jid','test@mid', '')
        database.set_status_by_jid('test@jid','enabled')
        users=database.get_users()
        mu={}
        for u in users:
            if not mu.get(u['mid']):
                mu[u['mid']]=list([u['jid']])
            else:
                mu[u['mid']].append(u['jid'])
        emu={
            'onemore@masto.test': ['user2@home.myhome'],
            'shura@mastodon.social': ['admin@lenovo.myhome', 'admin@home.myhome'],
            'test@mid':['test@jid']
            }
        self.assertEqual(mu,emu)
        user=database.get_user_by_jid('user2@home.myhome')
        sample={'jid': 'user2@home.myhome', 'status': 'enabled', 'token': '111', 'mid': 'onemore@masto.test', 'receive_replies':'1'}
        self.assertEqual(user,sample)
        user=database.get_user_by_jid('non-exist')
        self.assertEqual(user,None)
        masto_users=[]
        # for u in users:
        #     _=mastodon_listener.MastodonUser(u['mid'],u['token'])
        #     _.add_jids(mu[u['mid']])
        #     masto_users.append(_)
        # time.sleep(5)

    
    
    def disable_test_xmpp_users(self):
        tmp_db=USERS_TEST_DB+'.bak'
        copyfile(USERS_TEST_DB, tmp_db)
        database = db.Db(tmp_db)
        users=database.get_users()
        xmpp=gxmpp.Component('megagate.home.myhome', '123456', 'localhost', 5347)
        xmpp.register_plugin('xep_0030')  # Service Discovery
        xmpp.register_plugin('xep_0004')  # Data Forms
        xmpp.register_plugin('xep_0060')  # PubSub
        xmpp.register_plugin('xep_0199')  # XMPP Ping
        xmpp.add_users(users)
        self.assertEqual(users, xmpp.users)

    


    def disable_test_process_xmpp_thread1(self):
        S=self
        message={
            'jid':'admin@home.myhome',
            'to':'105254999743786130@mastodon.xmpp.ru',
            'body':"> @shura:\n> @Shura@pixelfed.social  @shura нормалды\nanswer"
        }
        class myMasto:
            def status_post(self, status, in_reply_to_id, visibility):
                print('status=', status)
                print('in_rely_to_id=', in_reply_to_id)
                print('visibility=',visibility)
                
                res=re.search(r'answer(.*)',status, flags=re.M|re.S)
                mentions_str=res.group(1)
                print(mentions_str)
                mentions=mentions_str.split(' ')
                mentions_ex=['']
                S.assertEqual(mentions, mentions_ex)
                print(mentions)
                
                return {
                    'url':'url',
                    'id':'id',
                    'created_at':datetime.utcnow()
                }
        m=myMasto()
        tmp_db=MESSAGES_TEST_DB+'.bak'
        copyfile(MESSAGES_TEST_DB, tmp_db)
        main.message_store=MessageStore(tmp_db)
        main.MESSAGES_DB = tmp_db
        main.users_db = db.Db(USERS_TEST_DB)
        main.USERS_DB=USERS_TEST_DB
        main.mastodon_listeners = {
            'shura@mastodon.social':m
        }
        main.process_xmpp_message_thread(message)
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass
        new_message=main.message_store.get_message_by_id('id')
        print("mentions")
        print(new_message['mentions'])
        self.assertEqual(new_message['mentions'],'@shura@mastodon.social @shura@pixelfed.social' )
        
    def disable_test_process_xmpp_thread2(self):
        S=self
        message={
            'jid':'L29Ah@qoto.org',
            'to':'107960344422410679@mastodon.xmpp.ru',
            'body':"> А слона-то (ссылку) я и не приметил. Но, правда, ничего не понял. :-)\nПо ссылке фото фотохромных очков, наполовину пролежавших полминуты под солнышком из окошка."
        }
        class myMasto:
            def status_post(self, status, in_reply_to_id, visibility):
                print('status=', status)
                print('in_rely_to_id=', in_reply_to_id)
                print('visibility=',visibility)                
                mentions=mentions_str.split(' ')
                mentions_ex=['']
                S.assertEqual(mentions, mentions_ex)
                print(mentions)
                return {
                    'url':'url',
                    'id':'id',
                }
        m=myMasto()
        tmp_db=MESSAGES_TEST_DB+'.bak'
        copyfile(MESSAGES_TEST_DB, tmp_db)
        main.message_store=MessageStore(tmp_db)
        main.users_db = db.Db(USERS_TEST_DB)
        main.USERS_DB=USERS_TEST_DB
        main.mastodon_listeners = {
            'shura@mastodon.social':m
        }
        main.process_xmpp_message_thread(message)
        new_message=main.message_store.get_message_by_id('107961941922050128')
        print(new_message)
        print(new_message['mentions'])
        self.assertEqual(new_message['mentions'],'@kinen@hubzilla.konzurovski.net ' )

    def disable_test_quotation(self):
        '''
        #### Quotation test ####
        '''
        S=self
        message={
            'jid':'admin@home.myhome',
            'to':'107903110563192732@mastodon.xmpp.ru',
            'body':"> Главный проект\nSaluton!\n> https://mycorrhiza.wiki\nВсе изменения в git? diff'ы читаемые?"
        }
        class myMasto:
            def status_post(self, status, in_reply_to_id, visibility):
                print('status=', status)
                print('in_rely_to_id=', in_reply_to_id)
                print('visibility=',visibility)
                return {
                    'url':'url',
                    'id':'id',
                    'created_at':datetime.now()
                }
        m=myMasto()
        tmp_db=MESSAGES_TEST_DB+'.bak'
        copyfile(MESSAGES_TEST_DB, tmp_db)
        main.message_store=MessageStore(tmp_db)
        main.users_db = db.Db(USERS_TEST_DB)
        main.USERS_DB = USERS_TEST_DB
        main.MESSAGES_DB = tmp_db
        main.TEST_MODE=1
        main.mastodon_listeners = {
            'shura@mastodon.social':m
        }
        print("MESSAGE")
        print(message)
        main.process_xmpp_message_thread(message)
        print("mentions")
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass
        new_message=main.message_store.get_message_by_id('id')
        print(new_message)
        self.assertEqual(new_message['message'],"@bouncepaw@lor.sh Saluton!\n> https://mycorrhiza.wiki\nВсе изменения в git? diff'ы читаемые?" )


    def disable_test_mysql_base(self):
        '''
        Basic Mysql test
        '''
        S=self
        self.maxDiff=None
        message_store = MysqlStore(
            MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USERNAME, MYSQL_PASSWORD)
        
        with open("mysql_dataset.csv") as csvfile:
            reader = csv.reader(csvfile)
            d = {}
            for line in reader:
                d['date'] = datetime.fromisoformat(line[6])
                d['mentions'] = line[2]
                d['url'] = line[1]
                d['visibility'] = line[3]
                d['id'] = line[4]
                d['message'] = line[0]
                d['mid'] = line[5]
                d['feed'] = line[7]
                n = message_store.get_message_by_id(line[4])
                n['date'] = n['date'].astimezone(timezone.utc)
                S.assertDictEqual(d, n)
    def test_get_messages_mysql(self):
        message_store = MysqlStore(
            MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USERNAME, MYSQL_PASSWORD)
        d = message_store.get_messages_for_user('shura@mastodon.social')
        t = ['104032314153599025', '104031984840402718', '104032564439980906', '104032626519236083', '104032640246088900', '104032712934805879', '104032776374773355', '104032809534204360', '105237775810751372']
        self.assertListEqual(t, d)


    def test_get_messagesby_thread_mysql(self):
        message_store = MysqlStore(
            MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USERNAME, MYSQL_PASSWORD)
        d = message_store.get_messages_for_user_by_thread('shura@mastodon.social','105254999743786130')
        t = ['105254999743786130', '105255000721266255', '105255003720699893', '105255007313424798', '106171834340437925', '106171880670024768']
        self.assertListEqual(t, d)
        # print("!!!!!!")
        # print(d)


if __name__ == '__main__':
    message_store = MysqlStore(MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USERNAME, MYSQL_PASSWORD)
    message_store.drop_database()
    message_store = MysqlStore(MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USERNAME, MYSQL_PASSWORD)
    with open("mysql_dataset.csv") as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            line[6] = datetime.fromisoformat(line[6])
            line[2] = line[2].split(' ')
            author = line[2][0]
            line[2] = set(line[2])
            message_store.add_message(
                line[0], line[1], author,
                line[2], line[3], line[4],
                line[5], line[6], line[7]
            )
    unittest.main()
    message_store.drop_database()
