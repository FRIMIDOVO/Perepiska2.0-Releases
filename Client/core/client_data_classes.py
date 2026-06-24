from dataclasses import dataclass


@dataclass
class Core:
    addr: tuple = None
    connector: object = None

@dataclass
class Handlers:
    sender_handler: object = None
    receiver_handler: object = None

@dataclass
class Protocols:
    auth_commands: object = None
    file_commands: object = None
    commands: object = None
    messages: object = None