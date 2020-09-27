DATABASES = {
    'nip': {
        'NAME': 'nip',
        'ENGINE': 'sql_server.pyodbc',
        'HOST': 'TUMS-NIP',
        'USER': 'sa',
        'PASSWORD': 'VI?9NHuvpj',

        'OPTIONS': {
                    'driver': 'SQL Server Native Client 11.0',
                }
    },

    'didgah': {
        'NAME': 'didgah',
        'ENGINE': 'sql_server.pyodbc',
        'HOST': '10.2.7.68',
        'USER': 'nipSA',
        'PASSWORD': 'VI?9NHuvpj',

        'OPTIONS': {
                    'driver': 'SQL Server Native Client 11.0',
                }
    }

}

def get_db():

    return DATABASES