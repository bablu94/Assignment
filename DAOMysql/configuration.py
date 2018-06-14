# CONTAINS DB CONFIG

import sys
sys.path.append('../')

class configuration:
    db_config = {}
    configString = ''

    def __init__(self):
        self.db_config = {
            "host" : "127.0.0.1",
            "port" : 3306,
            "username" : "root",
            "password" : "pass",
            "dbname" : "plivo"
        }

        self.configString = 'mysql://' + self.db_config['username'] + ':' + self.db_config['password'] + '@' + \
                            self.db_config['host'] + ':' + str(self.db_config['port']) + '/' + self.db_config['dbname']

    def getConfigString(self):
        if self.configString:
            return self.configString