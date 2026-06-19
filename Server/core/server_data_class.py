from dataclasses import dataclass


@dataclass
class Handlers:
    client_handler: object = None
    client_messages: object = None
    admin_bash: object = None
    admin_commands: object = None


@dataclass
class Managers:
    client_manager: object = None
    auth_manager: object = None