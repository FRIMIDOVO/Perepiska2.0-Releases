from dataclasses import dataclass


@dataclass
class Core:
    addr: tuple = None
    connector: object = None

@dataclass
class Handlers:
    sender_handler: object = None
    receiver_handler: object = None
    messages: object = None
    commands: object = None

@dataclass
class Managers:
    auth_manager: object = None