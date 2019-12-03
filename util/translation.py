from models.user import GenderType

def get_opening_greeting(user):
    """Creates an opening greeting string according to the users gender.
    :param user: The user to salute.
    :type user: str
    """
    if user.get_gender() == GenderType.FEMALE:
        return "Sehr geehrte Frau {}".format(user.get_name())
    return "Sehr geehrter Herr {}".format(user.get_name())
