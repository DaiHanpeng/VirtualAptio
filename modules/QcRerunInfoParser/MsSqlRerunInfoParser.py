from ..MsSqlServerManager.MsSqlServerManager import MsSqlServerManager
from ..Mqtt.MqttInterface import MqttInterface
from ..Logging.LoggingConfig import project_logger

import ConfigParser
import os
import datetime
import time
from threading import Timer

class QcRerunInfo():
    '''

    '''
    def __init__(self,creation_datetime,lot,instrument,test,status,update_datetime,wg_reule):
        self.creation_datetime = creation_datetime
        self.lot = lot
        self.instrument = instrument
        self.test = test
        self.status = status
        self.update_datetime = update_datetime
        self.wg_rule = wg_reule

    def __repr__(self):
        return ' creation datetime: '+str(self.creation_datetime)+','\
                ' lot: '+self.lot+','\
                ' instrument: '+self.instrument+','\
                ' test: '+self.test+','\
                ' status: '+self.status+','\
                ' update_datetime: '+str(self.update_datetime)+','\
                ' west guard rule: '+str(self.wg_rule)

class MsSqlQcRerunInfoProcessor():
    '''

    '''
    PARAMETER_INI_FILE = os.path.abspath('..')+'\\Config'+"\\Parameters.CFG"
    #PARAMETER_INI_FILE = os.path.abspath('../..')+'\\Config'+"\\Parameters.CFG"
    QC_RERUN_SECTION_NAME = r"QC Rerun"
    MS_SQL_SERVER = r'MS SQL Server'
    USER = r'User'
    PASSWORD = r'Password'
    DATABASE = r'Database'

    def __init__(self):
        self.qc_rerun_list = []

        self.ms_sql_server = ''
        self.ms_sql_user = ''
        self.ms_sql_password = ''
        self.ms_sql_database = ''

        self.last_update_timestamp = ''

        self.get_sql_server_connect_parameters()

    def get_sql_server_connect_parameters(self):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(MsSqlQcRerunInfoProcessor.PARAMETER_INI_FILE)

        if config_parser.has_section(MsSqlQcRerunInfoProcessor.QC_RERUN_SECTION_NAME):
            self.ms_sql_server = config_parser.get(MsSqlQcRerunInfoProcessor.QC_RERUN_SECTION_NAME, MsSqlQcRerunInfoProcessor.MS_SQL_SERVER)
            self.ms_sql_user   = config_parser.get(MsSqlQcRerunInfoProcessor.QC_RERUN_SECTION_NAME, MsSqlQcRerunInfoProcessor.USER)
            self.ms_sql_password = config_parser.get(MsSqlQcRerunInfoProcessor.QC_RERUN_SECTION_NAME, MsSqlQcRerunInfoProcessor.PASSWORD)
            self.ms_sql_database = config_parser.get(MsSqlQcRerunInfoProcessor.QC_RERUN_SECTION_NAME, MsSqlQcRerunInfoProcessor.DATABASE)

    def get_qc_rerun_list_from_ms_sql_server(self):
        self.qc_rerun_list = []

        with MsSqlServerManager(self.ms_sql_server, self.ms_sql_user, self.ms_sql_password, self.ms_sql_database) as ms_sql_server_manager:
            query_all_requested_qc_rerun = "SELECT * FROM QC WHERE \
            (TestStatus = 'R' OR TestStatus = 'A') AND (DATEDIFF(DAY,DATESTAMP,GETDATE()) < 1)"
            print query_all_requested_qc_rerun
            for result in ms_sql_server_manager.query(query_all_requested_qc_rerun):
                #print result
                creation_datetime = ''
                update_datetime = ''
                if isinstance(result[1],datetime.datetime):
                    creation_datetime = result[1].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(result[6],datetime.datetime):
                    update_datetime = result[6].strftime("%Y-%m-%d %H:%M:%S")
                if self.last_update_timestamp < update_datetime:
                    if creation_datetime and result[2] and result[3] and result[4] and result[5] and update_datetime:
                        self.qc_rerun_list.append(QcRerunInfo(creation_datetime,result[2],result[3],result[4],result[5],update_datetime,result[7]))

    def publish_mqtt_message(self):
        if self.qc_rerun_list:
            for info in self.qc_rerun_list:
                if isinstance(info,QcRerunInfo):
                    topic = 'mqtt'
                    payload = 'qc_rerun'+str(info)
                    message = 'topic: '+topic+", payload: "+payload+' published'
                    print message
                    project_logger.write_log_message(message)
                    #publish mqtt message.
                    MqttInterface.publish(topic,payload)
                    time.sleep(1)

    def update_last_update_timestamp(self):
        if self.qc_rerun_list:
            for info in self.qc_rerun_list:
                if isinstance(info,QcRerunInfo):
                    if info.update_datetime > self.last_update_timestamp:
                        self.last_update_timestamp = info.update_datetime

    def __repr__(self):
        return 'qc rerun list:\n' +\
               '\n'.join(str(item) for item in self.qc_rerun_list)


class MsSqlQcRerunInfoTimingProcessor(MsSqlQcRerunInfoProcessor):
    '''

    '''
    UPDATE_TIME_SPAN = r'TimeSpan'

    def __init__(self):
        self.update_time_span = 5
        self.update_parameters()

        self.timer = Timer(1*60,self.timing_exec_func)
        MsSqlQcRerunInfoProcessor.__init__(self)
        #self.timer.start()
        self.timing_exec_func()

    def cancel_timer(self):
        self.timer.cancel()

    def update_parameters(self):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(MsSqlQcRerunInfoProcessor.PARAMETER_INI_FILE)

        if config_parser.has_section(MsSqlQcRerunInfoProcessor.QC_RERUN_SECTION_NAME):
            self.update_time_span = config_parser.get(MsSqlQcRerunInfoProcessor.QC_RERUN_SECTION_NAME, MsSqlQcRerunInfoTimingProcessor.UPDATE_TIME_SPAN)

    def timing_exec_func(self):
        print 'qc rerun timing exec func start.'

        try:
            self.get_qc_rerun_list_from_ms_sql_server()
            self.publish_mqtt_message()
            self.update_last_update_timestamp()

            self.timer = Timer(1*60,self.timing_exec_func)
            self.timer.start()
        except Exception as e:
            print e


def test():
    parser = MsSqlQcRerunInfoProcessor()
    parser.get_qc_rerun_list_from_ms_sql_server()
    parser.publish_mqtt_message()
    print parser

if __name__ == '__main__':
    test()