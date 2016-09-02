import sys, os
sys.path.append(os.path.abspath('..'))

from modules.Mqtt.publisher import publisher
from modules.QcRerunInfoParser.QcRerunInfoParser import *

from modules.MsSqlServerManager.MsSqlServerManager import MsSqlServerManager
from modules.QcRerunInfoParser.MsSqlRerunInfoParser import MsSqlQcRerunInfoProcessor,MsSqlQcRerunInfoTimingProcessor

from modules.CriticalValueParser.CriticalValueParser import CriticalValueParser,CriticalValueTimingParser

def test():
    parser = QcRerunInfoParser()
    parser.parse()

    print parser

    publisher = QcRerunInfoMqttPublisher()
    publisher.publish(parser.get_rerun_list())

def test_qc_rerun_ms_sql_server_parser():
    parser = MsSqlQcRerunInfoProcessor()
    parser.get_qc_rerun_list_from_ms_sql_server()
    parser.publish_mqtt_message()

    print parser

def test_qc_rerun_ms_sql_server_timing_processor():
    MsSqlQcRerunInfoTimingProcessor()

def test_critical_parser():
    lis_out_log_folder = r'D:\01_Automation\23_Experiential_Conclusions_2016\23_Zhongshan\LIS_OUT_Translator'
    critical_info_parser = CriticalValueParser()
    critical_info_parser.parse_critical_value_info_from_log_file(lis_out_log_folder)
    print critical_info_parser

def test01():
    string = r'C|3|L|<2000.0&XA&Critical: <1200&XA&NS=-5&XA&IS=1&XA&QS=0&XA&DS=0|G'
    print string.startswith(r'C|')
    print string.endswith(r'|G')
    print string.find(r'Critical:') <> -1
    print string.startswith(r'C|') and (string.find(r'Critical:') <> -1) and string.endswith(r'|G')

def test02():
    CriticalValueTimingParser()

if __name__ == '__main__':
    test_qc_rerun_ms_sql_server_timing_processor()