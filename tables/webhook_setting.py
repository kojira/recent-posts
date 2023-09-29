from table_base import TableBase

class Interface(TableBase):
    CREATE_TABLE_SQL = '''\
    CREATE TABLE webhook_setting (
        id            INTEGER    PRIMARY KEY AUTOINCREMENT, --ID
        ctime         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  --created-time
        server_id     TEXT,                                 --サーバーの18桁ID
        category_name TEXT,                                 --カテゴリ名
        channels      TEXT,                                 --カンマ区切りの有効なチャンネル
        webhook_url   TEXT,                                 --ログ保存のwebhook url
        flag          INTEGER DEFAULT 0                     --0:有効 1:無効
    );
    '''

    def get_info(self):
        info = {
            "name": "webhook",
            "version": "0.0.1",
        }
        return info

    def insert(self, server_id, channels, category_name, webhook_url):
        self.cur.execute('INSERT INTO webhook_setting (server_id, channels, category_name, webhook_url) VALUES (?, ?, ?, ?)', (server_id, channels, category_name, webhook_url))
        self.con.commit()

    def select_by_server_id(self, server_id):
        self.cur.execute('SELECT * FROM webhook_setting WHERE server_id=? ORDER BY ctime DESC',(server_id,))
        setting_list = self.cur.fetchall()
        return setting_list

    def select_by_category_name(self, server_id, category_name):
        self.cur.execute('SELECT * FROM webhook_setting WHERE server_id=? AND category_name=? AND flag=0 ORDER BY ctime DESC LIMIT 1',(server_id,category_name))
        setting_list = self.cur.fetchone()
        return setting_list

    def select_all(self):
        self.cur.execute('SELECT * FROM webhook_setting WHERE flag=0 ORDER BY ctime DESC')
        setting_list = self.cur.fetchall()
        return setting_list

    def select_deleted(self, server_id, flag=0):
        self.cur.execute('SELECT * FROM webhook_setting WHERE flag=1 AND server_id=?',(server_id,))
        setting_list = self.cur.fetchall()
        return setting_list

    def update(self, server_id, category_name, webhook_url):
        self.cur.execute('UPDATE webhook_setting SET webhook_url=? WHERE category_name=? AND flag=0 AND server_id=?',(webhook_url, category_name, server_id))
        self.con.commit()

    def update_channels(self, server_id, category_name, channels):
        self.cur.execute('UPDATE webhook_setting SET channels=? WHERE category_name=? AND flag=0 AND server_id=?',(channels, category_name, server_id))
        self.con.commit()

    def logical_delete(self, server_id, category_name):
        self.cur.execute('UPDATE webhook_setting SET flag=1 WHERE server_id=? AND category_name=?',(server_id, category_name))
        self.con.commit()

