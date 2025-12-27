
HELP_MESSAGE = f'''HELP
. - open last message in separate chat dialog
.1 - open next-to-last message in separate chat dialog
.2 - open 3-rd to-last message ...
and so on up to 99-th message

r - reblog last message
r1 - reblog next-to-last message
r2 - reblog 3-rd to-last message
and so on up to 99-th message

f - favourite last message
f1 - favourite next-to-last message
f2 - favourite 3-rd to-last message
and so on up to 99-th message


w - get link to last message
w1 - get link to next-to-last message
and so on up to 99-th message

Also you can use quotation to point desired message.
For example:
    > @someuser@mastodon:
    > nice weather, isn't it?
    .
will open message with such text in separate chat dialog

Also reactions are possible.
👍 - reblog message
❤ or ★ - like message
💬 or 🗨 - open message thread

h - this help

Notes!
You cannot answer to massages from this chat directly. To answer to message please open it on separate chat dialog
You cannot write new messages in this chat. To make new massage please send it to new@{0} contact
'''

THREAD_HELP_MESSAGE = '''
HELP
---
w - get link
. - get full thread
m - get list of mentions
rr - reblog FIRST message in thread
h - this help
text - post answer on last message

> quotation
text
to post answer to desired status

> quotation
f
to favourite quoted post

> quotation
r
to reblog quoted post

---
Also reactions are possible.
👍 - reblog message
❤ or ★ - like message
'''

CONFIG_HELP_MESSAGE = '''
HELP
"server server.tld" - assign new mastodon instance
"disable" or "d" - temporary disable notifications
"enable" or "e" - enable notifications
"replies on" - show replies in home feed
"replies off" - do not show replies in home feed
"autoboost <mastodon id>" or "ab <mastodon id>" - enable autoboost for <mastodon id>
"info" or "i" - information about account
'''

SUBSCRIPTION_MESSAGE = '''
Please add this contact to your roster. The contact is for managing your mastodon account
Type 'help' for help
Please enter your mastodon server name with command 'server'. For example:
server mastodon.social
'''
