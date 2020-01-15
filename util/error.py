import json


class Error:
    """Represents an error which occurred in the application."""

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def to_json(self):
        return json.dumps(self.__dict__)


UNKNOWN_RESOURCE = Error('Unknown resource', 'This resource is not available.')
UNKNOWN_USER = Error('Unknown user', 'This user is not known.')
NO_USERS = Error('No users', 'There are no users in the database.')
UNKNOWN_GROUP = Error('Unknown group', 'This group is not known.')
NO_METER_ID = Error('No meter id', 'No meter id was received.')
MISSING_DISCOVERGY_CREDENTIALS = Error(
    'Missing discovergy credentials', 'Wrong or missing discovergy credentials.')
MISSING_DISAGGREGATION_DATA = Error(
    'Missing disaggregation data',
    'There is no data for the requested meter in the requested period.')
