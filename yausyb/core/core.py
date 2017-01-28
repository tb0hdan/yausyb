import collections
import Skype4Py

from yausyb import __title__
from yausyb.logger import logger
from yausyb.handlers.kernel import prepare_message

class BotCore(object):
    admins = []
    seen_id = collections.deque(maxlen = 10)

    def __init__(self, name=__title__):
        self.skype = Skype4Py.Skype(Events = self)
        self.skype.FriendlyName = name
        self.skype.Attach()

    # skype handlers
    def AttachmentStatus(self, status):
        if status == Skype4Py.apiAttachAvailable:
            skype.Attach()

    def send_msg(self, msg, message):
        try:
            # chat, via handle
            msg.Chat.SendMessage(message)
        except Exception as exc:
            try:
                # chat, via name
                self.send_chatroom(message, msg.Chat.Name)
            except:
                # private
                self.skype.SendMessage(message, msg.FromHandle)

    def MessageStatus(self, msg, status):
        if not status in (Skype4Py.cmsSending, Skype4Py.cmsSent, Skype4Py.cmsRead, Skype4Py.cmsReceived):
            logger.debug("[%s] %d SKIP", status, msg.Id)
            return
        if self.seen_id.count(msg.Id):
            logger.debug("[%s] %d DUP", status, msg.Id)
            return
        else:
            self.seen_id.append(msg.Id)
            chat_message = msg.Body.encode('utf-8')
            for line in chat_message.splitlines():
                message = prepare_message(line.strip())
                if message:
                    self.send_msg(msg, message)
            logger.debug('%s/%s -> %s', msg.Chat.Name, msg.FromHandle, msg.Body.encode('utf-8'))

    def send_chatroom(self, message, chatroom):
        chat = self.skype.Chat(Name=chatroom)
        chat.SendMessage(message)
