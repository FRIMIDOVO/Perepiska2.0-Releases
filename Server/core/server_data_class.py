from dataclasses import dataclass


@dataclass
class Handlers:
    client_handler: object = None
    admin_bash: object = None


@dataclass
class Managers:
    client_manager: object = None
    auth_manager: object = None

@dataclass
class Protocols:
    admin_commands: object = None
    client_messages: object = None