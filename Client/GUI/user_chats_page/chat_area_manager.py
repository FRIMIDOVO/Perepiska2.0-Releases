import logging


class ChatArea:
    def __init__(self, parent, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parent = parent
        self.Protocols = Protocols