from models.user import GenderType

def get_opening_greeting(user):
    """Creates an opening greeting string according to the users gender.
    :param str: The user to salute.
    """
    if user.gender == GenderType.FEMALE:
        return "Sehr geehrte Frau {}".format(user.name)
    return "Sehr geehrter Herr {}".format(user.name)
