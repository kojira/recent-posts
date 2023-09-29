from abc import *

class TableBase(object):
    __metaclass__ = ABCMeta
    CREATE_TABLE_SQL = ""

    def __init__(self, con, cursol):
        self.con = con
        self.cur = cursol

    def create_table(self):
        self.cur.execute(self.CREATE_TABLE_SQL)
        self.con.commit()

    @abstractmethod
    def get_info(self):
        raise NotImplementedError()

