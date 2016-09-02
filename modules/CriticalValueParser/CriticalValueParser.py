from threading import Timer
import ConfigParser
import os

from ..GetLatestFile.GetLatestFile import GetLatestFile
from ..Mqtt.MqttInterface import MqttInterface
from ..Logging.LoggingConfig import project_logger

class CriticalValueInfo():
    '''

    '''
    def __init__(self,sample,test,analyzer,result,timestamp,warn_message):
        self.sample = sample
        self.test = test
        self.analyzer = analyzer
        self.result = result
        self.timestamp = timestamp
        self.warn_message = warn_message

    def __repr__(self):
        return 'sample id: '+self.sample+', '+\
                'test: '+self.test+', '+\
                'analyzer: '+self.analyzer+', '+\
                'result: '+self.result+', '+\
                'timestamp: '+self.timestamp+', '+\
                'warn_message: '+self.warn_message


class CriticalValueParser():
    '''

    '''
    MATCHING_STATUS = {'CriticalComment':1,'Result':2,'Sample':3}
    def __init__(self):
        self.critical_value_info_list = []
        self.last_updated_timestamp = ''
        self.matching_status = CriticalValueParser.MATCHING_STATUS['CriticalComment']

    def parse_critical_value_info_from_log_file(self,log_folder):
        latest_log_file = None
        self.critical_value_info_list = []
        file_content_list = []

        if log_folder:
                latest_log_file = GetLatestFile.get_latest_file(log_folder,'','.log')

        print latest_log_file

        if latest_log_file:
            # read file content into list.
            log_file_handler = None
            try:
                log_file_handler = open(latest_log_file,mode='rU')
                file_content_list = log_file_handler.readlines()
            except Exception as e:
                print e
                print 'file read failed!'
            finally:
                if log_file_handler:
                    log_file_handler.close()

        file_content_list.reverse()

        latest_timestamp = ''

        test = ''
        analyzer = ''
        result = ''
        timestamp = ''
        warn_message = ''

        print 'len of file content list: ', len(file_content_list)

        self.matching_status = CriticalValueParser.MATCHING_STATUS['CriticalComment']
        parsed_critical_info_list = []
        critical_value_matched = False
        for line in file_content_list:
            if isinstance(line,str):
                #update latest_timestamp
                if line.find(r'***') <> -1:
                    line_timestamp = line.split(r']')[1].strip()

                    if not latest_timestamp:
                        latest_timestamp = line_timestamp
                        print 'lates time stamp: ', latest_timestamp

                    if line_timestamp <= self.last_updated_timestamp:
                        break
                elif CriticalValueParser.MATCHING_STATUS['CriticalComment'] == self.matching_status and \
                        line.startswith(r'C|') and (line.find(r'Critical:') <> -1) and line.endswith('|G\n'):
                    self.matching_status = CriticalValueParser.MATCHING_STATUS['Result']
                    warn_message = line.split(r'Critical:')[1].strip()
                    if warn_message.find(r'&XA&') <> -1:
                        warn_message = warn_message.split(r'&XA&')[0].strip()
                    else:
                        warn_message = warn_message.split('|G')[0].strip()
                elif (CriticalValueParser.MATCHING_STATUS['Result'] == self.matching_status) \
                        and line.startswith(r'R|'):
                    self.matching_status = CriticalValueParser.MATCHING_STATUS['CriticalComment']

                    test = line.split(r'^^^')[1].split(r'^')[0].strip()
                    analyzer = line.split(r'||')[-1].strip()
                    result = line.split(r'|')[3].strip()
                    timestamp = line.split(r'|')[-3].strip()

                    parsed_critical_info_list.append(CriticalValueInfo('',test,analyzer,result,timestamp,warn_message))
                    critical_value_matched = True
                    # clear temp vars
                    test = ''
                    analyzer = ''
                    result = ''
                    timestamp = ''
                    warn_message = ''
                elif True == critical_value_matched and line.startswith(r'O|') and line.endswith('|||||||||F\n'):
                    critical_value_matched = False
                    sample_id =  line.split(r'|')[2].strip()
                    for item in parsed_critical_info_list:
                        if isinstance(item,CriticalValueInfo):
                            item.sample = sample_id
                            self.critical_value_info_list.append(item)
                    parsed_critical_info_list = []

        if latest_timestamp and latest_timestamp > self.last_updated_timestamp:
            self.last_updated_timestamp = latest_timestamp

    def publish_mqtt_message(self):
        for info in self.critical_value_info_list:
            if isinstance(info,CriticalValueInfo):
                topic = 'mqtt'
                payload = 'critical value: '+\
                          'sample id: '+info.sample+\
                          ',test: '+info.test+\
                          ', analyzer: '+info.analyzer+\
                          ',result; '+info.result+\
                          ',warn message: '+info.warn_message+\
                          ',timestamp: '+info.timestamp
                message = 'topic: '+topic+", payload: "+payload+' published'
                print message
                project_logger.write_log_message(message)
                MqttInterface.publish(topic,payload)

    def __repr__(self):
        return 'Critical Info List:\n'+'\n'.join(str(info) for info in self.critical_value_info_list)


class CriticalValueTimingParser(CriticalValueParser):
    '''

    '''
    PARAMETER_INI_FILE = os.path.abspath('..')+'\\Config'+"\\Parameters.CFG"
    SECTION_NAME = r"Communication"
    LOG_PATH = r'Lis Out Log Path'

    def __init__(self):
        self.lis_log_path = ""
        self.get_log_path()

        CriticalValueParser.__init__(self)

        self.timer = Timer(1*60,self.timing_exec_func)
        #self.timer.start()
        self.timing_exec_func()

    def timing_exec_func(self):
        print 'critical value parser timing exec func start.'

        try:
            self.parse_critical_value_info_from_log_file(self.lis_log_path)
            self.publish_mqtt_message()

            self.timer = Timer(1*60,self.timing_exec_func)
            self.timer.start()
        except Exception as e:
            print e

    def cancel_timer(self):
        self.timer.cancel()

    def get_log_path(self):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(CriticalValueTimingParser.PARAMETER_INI_FILE)

        if config_parser.has_section(CriticalValueTimingParser.SECTION_NAME):
            self.lis_log_path = config_parser.get(CriticalValueTimingParser.SECTION_NAME, CriticalValueTimingParser.LOG_PATH)




