import ConfigParser
import os
import time

from ..Mqtt.publisher import publisher


'''
definition of rerun list file structure.
creation time,qc lot,instrument,[test;status;timestamp],[test;status;timestamp],[test;status;timestamp],...
'''

class TestStatus():
    '''
    Test Staus Definition.
    '''
    def __init__(self,test,status,time_stamp):
        self.test = test
        self.status = status
        self.time_stamp = time_stamp

    def __repr__(self):
        return ' test: ' + self.test + ', status: ' + self.status + ', timestamp: ' + self.time_stamp

class QcRerunInfo():
    '''
    Qc Rerun Info Structure.
    '''
    def __init__(self,creation_time,lot,instrument,test_list):
        self.creation_time = creation_time
        self.lot = lot
        self.instrument = instrument
        self.test_list = test_list

    def __repr__(self):
        return 'creation time: ' + self.creation_time + \
               ' lot: ' + (str(self.lot)) + ', instrument: ' + \
               (str(self.instrument)) + ', test list: ' + \
               ','.join(str(test) for test in self.test_list)


class QcRerunInfoParser():
    '''
    parser of rerun list.
    '''
    PARAMETER_INI_FILE = os.path.abspath('..')+'\\Config'+"\\Parameters.CFG"
    #PARAMETER_INI_FILE = os.path.abspath('../..')+'\\Config'+"\\Parameters.CFG"
    QC_RERUN_SECTION_NAME = r"QC Rerun"
    FILE_PATH = r'File Path'

    def __init__(self):
        self.qc_rerun_list = []

        self.qc_rerun_file_path = None
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(QcRerunInfoParser.PARAMETER_INI_FILE)
        if config_parser.has_section(QcRerunInfoParser.QC_RERUN_SECTION_NAME):
            self.qc_rerun_file_path = config_parser.get(QcRerunInfoParser.QC_RERUN_SECTION_NAME,QcRerunInfoParser.FILE_PATH)


    def parse(self):
        print 'qc rerun file: ', self.qc_rerun_file_path
        if self.qc_rerun_file_path and os.path.isfile(self.qc_rerun_file_path):

            # read file content into list.
            try:
                qc_rerun_file_handler = open(self.qc_rerun_file_path)
                file_content_list = qc_rerun_file_handler.readlines()
            except Exception as e:
                print 'file read failed!'
            finally:
                qc_rerun_file_handler.close()

            if file_content_list:
                for line in file_content_list:
                    info_list = []
                    creation_time = ''
                    lot = ''
                    instrument = ''
                    test_list = []
                    if isinstance(line,str):
                        info_list = line.split(',')
                        if len(info_list) > 3:
                            creation_time = info_list[0].strip()
                            lot = info_list[1].strip()
                            instrument = info_list[2].strip()
                            if(lot and instrument):
                                for test_status_info in info_list[3:]:
                                    test_status_list = []
                                    if isinstance(test_status_info,str):
                                        test_status_list = test_status_info.split(';')
                                        if len(test_status_list) == 3:
                                            test = test_status_list[0].strip()
                                            status = test_status_list[1].strip()
                                            time_stamp = test_status_list[2].strip()
                                            test_list.append(TestStatus(test,status,time_stamp))
                            self.qc_rerun_list.append(QcRerunInfo(creation_time,lot,instrument,test_list))

    def get_rerun_list(self):
        return self.qc_rerun_list

    def __repr__(self):
        return 'rerun info list: \n' + '\n'.join(str(info) for info in self.qc_rerun_list)


class QcRerunInfoMqttPublisher():
    '''

    '''
    PARAMETER_INI_FILE = os.path.abspath('..')+'\\Config'+"\\Parameters.CFG"
    MQTT_SECTION_NAME = r"MQTT"
    SERVER = r'Server'
    PORT = r'Port'

    def __init__(self):
        self.server = ''
        self.port = ''

        config_parser = ConfigParser.ConfigParser()
        config_parser.read(QcRerunInfoMqttPublisher.PARAMETER_INI_FILE)
        if config_parser.has_section(QcRerunInfoMqttPublisher.MQTT_SECTION_NAME):
            self.server = config_parser.get(QcRerunInfoMqttPublisher.MQTT_SECTION_NAME,QcRerunInfoMqttPublisher.SERVER)
            self.port = config_parser.get(QcRerunInfoMqttPublisher.MQTT_SECTION_NAME,QcRerunInfoMqttPublisher.PORT)

    def publish(self,rerun_info_list):
        if isinstance(rerun_info_list,list) and len(rerun_info_list) > 0:
            for info in rerun_info_list:
                if isinstance(info,QcRerunInfo):
                    topic = 'clark'
                    payload = ','.join([info.creation_time,info.lot,info.instrument])+','+','.join(str(test) for test in info.test_list)
                    if(self.server and self.port):
                        publisher.publish(topic=topic,payload=payload,hostname=self.server,port=self.port)


def test():
    parser = QcRerunInfoParser()
    parser.parse()

    print parser

    #publisher = QcRerunInfoMqttPublisher()
    #publisher.publish(parser.get_rerun_list())

if __name__ == '__main__':
    test()




