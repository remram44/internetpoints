from datetime import datetime
import os

try:
    os.remove('database.sqlite3')
except OSError:
    print "!!!\nNOT removed database\n!!!"

from internetpoints.models import Poster, PosterEmail, Thread, Message, Task,\
    TaskAssignation
from internetpoints.storage import Session


if __name__ == '__main__':
    sqlsession = Session()

    remram = Poster(name='Remram')
    sqlsession.add(remram)
    sqlsession.commit()

    remirampin = PosterEmail(address='remram@gmail.com', poster=remram)
    sqlsession.add(remirampin)
    remram_fr = PosterEmail(address='remram@remram.fr', poster=remram)
    sqlsession.add(remram_fr)
    sqlsession.commit()

    devel = Poster(name='Developer')
    sqlsession.add(devel)
    devel_rez = PosterEmail(address='developer@someplace.com', poster=devel)
    sqlsession.add(devel_rez)
    sqlsession.commit()

    dates = [datetime.fromtimestamp(1390760000 + t*200000)
             for t in xrange(10)]

    t1 = Thread(last_msg=dates[1])
    t2 = Thread(last_msg=dates[5])
    sqlsession.add(t1)
    sqlsession.add(t2)
    sqlsession.commit()

    msg1_1 = Message(id='msg-id-1-1', from_='one',
                     subject='Test', text="Hello?",
                     thread=t1, date=dates[0])
    sqlsession.add(msg1_1)
    msg1_2 = Message(id='msg-id-1-2', from_='remram@remram.fr',
                     subject='Re: Test', text="Yep?",
                     thread=t1, date=dates[1])
    sqlsession.add(msg1_2)
    msg2_1 = Message(id='google-mail-bla-bla-2-1', from_='three',
                     subject='Bla', text="You have won woohoo",
                     thread=t2, date=dates[2])
    sqlsession.add(msg2_1)
    msg2_2 = Message(id='google-mail-bla-bla-2-2', from_='four',
                     subject='hehe (was: Bla)',
                     text="Trolling enlargement",
                     thread=t2, date=dates[3])
    sqlsession.add(msg2_2)
    msg2_3 = Message(id='google-mail-bla-bla-2-3', from_='developer@someplace.com',
                     subject='Re: hehe', text="Account in Africa\n<b>Not HTML</b>",
                     thread=t2, date=dates[4])
    sqlsession.add(msg2_3)
    msg2_4 = Message(id='google-mail-bla-bla-2-4', from_='remram@gmail.com',
                     subject='Re: Bla', text="Spamfilter doesn't work :(",
                     thread=t2, date=dates[5])
    sqlsession.add(msg2_4)
    sqlsession.commit()

    task1 = Task(name='task1', reward=3)
    sqlsession.add(task1)
    task2 = Task(name='task2', reward=5)
    sqlsession.add(task2)
    sqlsession.commit()

    t1_task1 = TaskAssignation(thread=t1, task=task1, poster=remram)
    sqlsession.add(t1_task1)
    t1_task2 = TaskAssignation(thread=t1, task=task2, poster=remram)
    sqlsession.add(t1_task2)
    remram.score = task1.reward + task2.reward
    sqlsession.add(remram)
    sqlsession.commit()
