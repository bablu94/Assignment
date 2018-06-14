import sys
import MySQLdb
from DAOMysql.configuration import configuration
import threading

sys.path.append('../')

config = configuration()

class Mysql:
    db = ''
    cursor = ''

    def __init__(self):
        lock = threading.Lock()
        with lock:
            if self.db and self.cursor:
                return
            else:
                self.db = MySQLdb.connect(host=config.db_config['host'], port=config.db_config['port'],
                                          user=config.db_config['username'], passwd=config.db_config['password'],
                                          db=config.db_config['dbname'])
                self.cursor = self.db.cursor()


    def getDbObject(self):
        if self.db and self.cursor:
            return self.cursor

        return None