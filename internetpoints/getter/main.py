from datetime import datetime
from email.header import decode_header
from email.parser import Parser
import email.utils
import logging
from poplib import POP3, POP3_SSL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import warnings

from internetpoints import config, models
from internetpoints.storage import Session


logger = logging.getLogger(__name__)


def get_messages(host, use_ssl, port, user, password):
    logger.info("Connecting to POP3 server %s:%d, using SSL: %s" % (
                 host, port, "yes" if use_ssl else "no"))

    if use_ssl:
        server = POP3_SSL(host, port)
    else:
        server = POP3(host, port)

    server.user(user)
    server.pass_(password)

    messages, total = server.stat()
    logger.info("Server has %d new messages (total %d)" % (messages, total))
    for i in xrange(messages):
        yield '\n'.join(server.retr(i+1)[1])

    server.quit()


def decode_subject(subject):
    res = []
    for text, charset in decode_header(subject):
        if charset:
            res.append(text.decode(charset, 'replace'))
        else:
            res.append(text.decode('ascii', 'replace'))
    return ' '.join(res)


def main():
    logging.basicConfig(level=logging.INFO)

    host, use_ssl, port, user, password = config.INBOX
    if callable(user):
        user = user()
    if callable(password):
        password = password()

    for msg in get_messages(host, use_ssl, port, user, password):
        # Feed it to Python's standard RFC 2822-based message parser
        parser = Parser()
        msg = parser.parsestr(msg)

        # Headers of interest
        msgid = msg['Message-ID']
        replyto = msg['In-Reply-To']
        subject = decode_subject(msg['Subject'])
        from_ = email.utils.parseaddr(msg['From'])[1]
        date = email.utils.parsedate_tz(msg['Date'])
        if date:
            date = datetime.fromtimestamp(email.utils.mktime_tz(date))

        logger.debug("Parsing message from %r" % (from_,))

        # Find text content
        if msg.is_multipart():
            logger.debug("Message is multipart with %d parts" % (
                        len(msg.get_payload()),))
            # RFC 2046 says that the last part is preferred
            text = None
            is_html = True
            for part in msg.get_payload():
                if part.get_content_type() == 'text/plain' or (
                        part.get_content_type() == 'text/html' and is_html):
                    charset = part.get_charsets()[0]
                    text = part.get_payload(decode=True).decode(charset,
                                                                'replace')
                    is_html = part.get_content_type() == 'text/html'
            if text is not None:
                logger.debug("Found a text part (text/%s)" % (
                            'html' if is_html else 'plain'),)
            else:
                logger.debug("Didn't find a text part")
            if text is None:
                text = msg.preamble
                is_html = False
                if text:
                    logger.debug("Using preamble")
        else:
            charset = msg.get_charsets()[0]
            text = msg.get_payload(decode=True).decode(charset,
                                                        'replace')
            content_type = msg.get_content_type()
            is_html = content_type == 'text/html'
            logger.debug("Message is not multipart (%s)" % (content_type,))

        if not text:
            logger.warning("Message from %r has no text!" % (from_,))
            text = "(No text content found)"
        elif is_html:
            try:
                import html2text
            except ImportError:
                warnings.warn("Can't convert HTML to text -- html2text "
                              "library not found")
            else:
                logger.debug("Converting HTML with html2text")
                h = html2text.HTML2Text()
                text = h.handle(text)
            is_html = False

        # Find thread this message is a part of
        sqlsession = Session()
        thread = None
        if replyto:
            try:
                parent_msg = (sqlsession.query(models.Message)
                                        .filter(models.Message.id == replyto)
                                        .one())
            except NoResultFound:
                pass
            else:
                thread = parent_msg.thread
                logger.debug("Message is part of existing thread %d" % (
                             thread.id,))
        if thread is None:
            thread = models.Thread(last_msg=date)
            thread_created = True
            sqlsession.add(thread)
        else:
            thread_created = False
            # FIXME : This should be synchronized somehow
            # Update last_msg date field
            if thread.last_msg < date:
                thread.last_msg = date
                sqlsession.add(thread)

        # Insert message
        message = models.Message(id=msgid, thread=thread, date=date,
                                 from_=from_,
                                 subject=subject, text=text)
        sqlsession.add(message)
        try:
            sqlsession.commit()
        except IntegrityError:
            sqlsession.rollback()
            logger.info("Got IntegrityError inserting message, skipping")
        else:
            if thread_created:
                logger.debug("Created new thread %d" % (thread.id,))
