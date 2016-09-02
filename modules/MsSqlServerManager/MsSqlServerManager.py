import pymssql

class MsSqlServerManager():
    '''

    '''
    def __init__(self,host,user,password,database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.conn = None

    def connect(self):
        if not self.database:
            raise (NameError,'no ms_sql_database')

        try:
            print 'ms sql connect parameters:'
            print self.host, self.user,self.password,self.database
            self.conn = pymssql.connect(self.host,self.user,self.password,self.database)
            print 'conntion initialize: ',self.conn
        except:
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def query(self,sql_query):
        if sql_query and self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            return cursor.fetchall()
        else:
            print sql_query
            print 'connction: ', self.conn
            print 'query failed!'

    def update(self,sql_update):
        if sql_update and self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_update)
            self.conn.commit()
            return cursor._result

    def insert(self,sql_insert,value_list):
        if sql_insert and self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_insert,value_list)
            self.conn.commit()
            return cursor._result


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            print 'connection closed.'

def test():
    import datetime

    with MsSqlServerManager('192.168.10.225','qc','qc','QC_DATA') as ms_sql_server_connct:
        query_all = r"SELECT * FROM QC"
        #print ms_sql_server_connct.query(query_all)
        for result in ms_sql_server_connct.query(query_all):
            print result

        #insert_sql = r"INSERT INTO QC(DATE,QCLot,InstrumentName,TestName,TestStatus,DateStamp) VAlUES(%s,%s,%s,%s,%s,%s)"
        #date_time = str(datetime.datetime.now())
        #print ms_sql_server_connct.insert(insert_sql,(date_time,'223344','Advia2400_1','Alb','R',date_time))

if __name__ == '__main__':
    test()