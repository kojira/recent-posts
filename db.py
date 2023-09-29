# -*- coding: utf-8 -*-

import sqlite3
import datetime
import os

from importlib import machinery


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Manager:
    def __init__(self, config):
        self.load_config(config)


    def load_config(self, db_file):
        self.db_file = db_file
        self.con = sqlite3.connect(self.db_file)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
        self.tables = {}
        self.load_tables()


    def load_tables(self):
        table_names = [
                "webhook_setting",
            ]

        for table in table_names:
            loader = machinery.SourceFileLoader(table, 'tables/'+table+'.py')
            module = loader.load_module()
            table_instance = module.Interface(self.con, self.cur)
            if not self.exist_table(table):
                table_instance.create_table()

            self.tables[table] = table_instance
            print("load table",table_instance.get_info())


    def exist_table(self, table_name):
        CHECK_TABLE_SQL = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cur.execute(CHECK_TABLE_SQL,(table_name,))
        columns = self.cur.fetchone()
        if columns is not None:
            return True
        return False

