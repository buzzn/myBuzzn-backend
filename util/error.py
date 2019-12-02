import json

class Error:
    """Represents an error which occurred in the application."""
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def to_json(self):
        return json.dumps(self.__dict__)

UNKNOWN_RESOURCE = Error('Unknown resource', 'This resource is not available.')
