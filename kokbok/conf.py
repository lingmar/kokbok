import os


def get_db_conf():
    """
    Return a suitable config dict from the relevant environment variables.
    """

    dbconf = {"host": os.getenv('KOK_DB_HOST', 'localhost'),
              "db": os.getenv('KOK_DB_NAME', "KOKBOK")}

    port = os.getenv('KOK_DB_PORT', None)
    user = os.getenv('KOK_DB_USER', None)
    password = os.getenv('KOK_DB_PASSWORD', None)

    if port:
        dbconf['port'] = int(port)
    if user:
        dbconf['user'] = user
    if password:
        dbconf['passwd'] = password

    return dbconf
