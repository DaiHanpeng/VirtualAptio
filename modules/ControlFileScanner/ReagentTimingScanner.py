import os
from threading import Timer
import ConfigParser
from PyQt4 import QtCore

from .ControlFileScanner import ControlFileScanner
from ..AptioReagent.AptioSystemReagentDialog import *
from ..ASTM.AstmThreadedClient import AstmThreadedClientManager
from ..FlagInfo.SampleFlagInfo import *
from ..Logging.LoggingConfig import project_logger
from .TimingScanner import TimingScanner
from ..TestMapParser.TestMapParser import AptioTestMap
from ..QcRerunInfoParser.MsSqlRerunInfoParser import MsSqlQcRerunInfoProcessor, MsSqlQcRerunInfoTimingProcessor
from ..CriticalValueParser.CriticalValueParser import CriticalValueTimingParser
from ..Mqtt.MqttInterface import MqttInterface

PARAMETER_INI_FILE = os.path.abspath('..')+'\\Config'+"\\Parameters.CFG"
COMMUNICATION_SECTION_NAME = "Communication"
HOST_ADDRESS = "Host Address"
CONNECT_PORT = "Connect Port"
FLEXLAB36_CONTROL_FOLDER_PATH = "Flexlab36 Control Folder Path"
TEST_MAP_INI_FILE_PATH = 'Test-Map File Path'

FILE_SCAN_INTERVAL = 20 # scan control log file time interval in seconds

#reagent status to flag parameters
INSTRUMENT_MAPPING_SECTION = 'Instrument Mapping'

REAGENT_FLAG_SECTION = 'Reagent Flag'
REAGENT_FLAG_GREEN = 'Green'
REAGENT_FLAG_YELLOW = 'Yellow'
REAGENT_FLAG_RED = 'Red'

class ReagentTimingScanner(ControlFileScanner,AptioSystemReagentDialog):
    update_gui_signal = pyqtSignal(AptioReagentInfo)
    def __init__(self):
        self.control_folder = ""
        self.test_map_ini_file_path = ""
        #self.host_address = ''
        #self.connect_port  = 8888
        self.instrument_mapping = {}
        self.reagent_flag_green = 'G'
        self.reagent_flag_yellow = 'Y'
        self.reagent_flag_red = 'R'

        self.load_communication_parameters_from_config_file()
        self.astm_client = AstmThreadedClientManager.get_astm_client()
        self.test_map_info = AptioTestMap()

        ControlFileScanner.__init__(self, self.control_folder)
        #TimingScanner.__init__(self)
        AptioSystemReagentDialog.__init__(self,self.aptio_reagent_info)
        self.update_gui_signal.connect(self.update_reagent_tree)
        self.timer = Timer(FILE_SCAN_INTERVAL,self.timing_exec_func)

        # start another timing scheduler to scan sample in-labbing position.
        self.sample_inlabbing_timing_scanner = TimingScanner()

        #start timing scheduler to scan qc rerun message
        self.qc_rerun_info_processor = MsSqlQcRerunInfoTimingProcessor()

        # critical parser
        self.critical_parser = CriticalValueTimingParser()

        #self.connect(self.ui.gridLayout,QtCore.SIGNAL("destroyed()"),self,QtCore.SLOT("on_window_destroyed()"))
        #self.ui.treeWidget.destroyed.connect(self.on_window_destroyed)

        #important!!!
        self.ui.closeEvent = self.closeEvent

    #@QtCore.pyqtSlot()
    def on_window_destroyed(self):
        self.timer.cancel()
        self.sample_inlabbing_timing_scanner.cancel_timer()
        self.qc_rerun_info_processor.cancel_timer()
        self.critical_parser.cancel_timer()

    def closeEvent(self, QCloseEvent):
        self.on_window_destroyed()

    def timing_exec_func(self):
        self.read_control_file_contents()
        self.clear_sample_flag_info_list()
        #self.scan_control_file_for_position_info()
        #self.construct_sample_flag_from_position()
        #self.send_flag_info()
        self.scan_control_file_for_reagent_info()

        #update instrument name.
        self.updadte_instrument_name()

        # gui must be run in main thread in qt, and can not be call outside the main thread.
        # so we emit signal here to notify the gui thread to update the displaying widget.
        # self.update_reagent_tree(self.aptio_reagent_info)
        self.update_gui_signal.emit(self.aptio_reagent_info)

        #update test map info
        self.test_map_info.build_test_map_from_ini_file(self.test_map_ini_file_path)

        # send reagent info via ASTM channel
        self.aptio_reagent_info_processing()

        #send flag to Centralink System.
        self.send_flag_info()

        #send mqtt notification
        self.send_mqtt_message()

        self.timer = Timer(FILE_SCAN_INTERVAL,self.timing_exec_func)

        self.timer.start()

    def updadte_instrument_name(self):
        for instrument in self.aptio_reagent_info.reagent_info_table:
            if isinstance(instrument,InstrumentReagentInfo):
                instrument.instrument_name = self.instrument_mapping[instrument.instrument_id]


    def send_flag_info(self):
        for sample_flag_info in self.sample_flag_info_list:
            self.astm_client.send_sample_las_flag(sample_flag_info)
            print sample_flag_info
            project_logger.write_log_message(str(sample_flag_info))
        #self.astm_client.trigger_a_sending()

    def send_mqtt_message(self):
        for sample_flag_info in self.sample_flag_info_list:
            if isinstance(sample_flag_info,SampleFlagInfo):
                topic = 'mqtt'
                flag = 'GREEN'
                if self.reagent_flag_red == sample_flag_info.flag:
                    flag = 'RED'
                elif self.reagent_flag_yellow == sample_flag_info.flag:
                    flag = 'YELLOW'
                payload = 'reagent,'+sample_flag_info.sample_id+','+sample_flag_info.Description+','+\
                          flag+','+sample_flag_info.time_stamp
                #only yellow and red flags will be published.
                if self.reagent_flag_green <> sample_flag_info.flag:
                    MqttInterface.publish(topic,payload)
                    message = 'topic: '+topic+", payload: "+payload+' published'
                    print message
                    project_logger.write_log_message(message)

    def reagent_status_2_flag(self,reagent_status):
        flag = 'undefined'
        if reagent_status == GREEN:
            flag = self.reagent_flag_green
        elif reagent_status == YELLOW:
            flag = self.reagent_flag_yellow
        elif reagent_status == RED:
            flag = self.reagent_flag_red
        return flag

    def aptio_reagent_info_processing(self):
        for instrInfo in self.aptio_reagent_info.reagent_info_table:
            if isinstance(instrInfo, InstrumentReagentInfo):
                for reagent in instrInfo.reagent_info_list:
                    if isinstance(reagent, ReagentInfoItem):
                        if reagent.reagent_status <> reagent.pre_reagent_status:
                            flag = 'undefined'
                            flag = self.reagent_status_2_flag(reagent.reagent_status)
                            flag_info = SampleFlagInfo(sample_id=self.instrument_mapping[instrInfo.instrument_id],flag=flag,time_stamp=instrInfo.time_stamp,descrip=reagent.reagent_name)

                            self.sample_flag_info_list.append(flag_info)
                            '''
                            if True == self.test_map_info.is_test_enabled_in_instrument(str(reagent.reagent_name),str(instrInfo.instrument_id)):
                                self.sample_flag_info_list.append(flag_info)
                            else:
                                print str(reagent.reagent_name),str(instrInfo.instrument_id)
                                project_logger.write_log_message(flag_info)
                            '''

                            #print reagent
                            #project_logger.write_log_message(str(reagent))

    def start_timing_scanner(self):
        self.timer.start()

    def load_communication_parameters_from_config_file(self):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(PARAMETER_INI_FILE)

        if config_parser.has_section(COMMUNICATION_SECTION_NAME):
            #self.host_address = config_parser.get(COMMUNICATION_SECTION_NAME,HOST_ADDRESS)
            #self.connect_port = config_parser.getint(COMMUNICATION_SECTION_NAME,CONNECT_PORT)
            self.control_folder = config_parser.get(COMMUNICATION_SECTION_NAME, FLEXLAB36_CONTROL_FOLDER_PATH)
            self.test_map_ini_file_path = config_parser.get(COMMUNICATION_SECTION_NAME,TEST_MAP_INI_FILE_PATH)

        if config_parser.has_section(INSTRUMENT_MAPPING_SECTION):
            instrument_mapping_list = config_parser.items(INSTRUMENT_MAPPING_SECTION)
            if instrument_mapping_list:
                for item in instrument_mapping_list:
                    self.instrument_mapping[item[0]] = item[1]

        if config_parser.has_section(REAGENT_FLAG_SECTION):
            self.reagent_flag_green = config_parser.get(REAGENT_FLAG_SECTION,REAGENT_FLAG_GREEN)
            self.reagent_flag_yellow = config_parser.get(REAGENT_FLAG_SECTION,REAGENT_FLAG_YELLOW)
            self.reagent_flag_red = config_parser.get(REAGENT_FLAG_SECTION,REAGENT_FLAG_RED)

if __name__ == "__main__":
    scanner = ReagentTimingScanner()
    scanner.start_timing_scanner()
