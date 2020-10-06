DATABASES = {
    'default': {
        'NAME': 'nip',
        'ENGINE': 'sql_server.pyodbc',
        'HOST': 'TUMS-NIP',
        'USER': 'sa',
        'PASSWORD': 'VI?9NHuvpj',
        'OPTIONS': {
                    'driver': 'SQL Server Native Client 11.0',
                }
    }
}

def get_db():

    return DATABASES