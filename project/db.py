DATABASES = {
    'default': {
        'NAME': 'nip',
        'ENGINE': 'sql_server.pyodbc',
        'HOST': 'TUMS-NIP',
        'USER': 'sa',
        'PASSWORD': '1qaz!QAZ',

        'OPTIONS': {
                    'driver': 'SQL Server Native Client 11.0',
                }
    }
}

def get_db():

    return DATABASES