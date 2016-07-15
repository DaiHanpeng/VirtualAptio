import threading
from socket import *
from ASTM import *

#from os import sys,path
#sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
import ConfigParser
import os
import time

from ..InlabbingPosition.SampleInlabbingPosition import *
from ..FlagInfo.SampleFlagInfo import *
from ..Logging.LoggingConfig import project_logger


PARAMETER_INI_FILE = os.path.abspath('..')+'\\Config'+"\\Parameters.CFG"
COMMUNICATION_SECTION_NAME = "Communication"
HOST_ADDRESS = "Host Address"
CONNECT_PORT = "Connect Port"

RECEIVING_BUFFER_SIZE = 1024


class AstmThreadedClient(object):
    """
    this class is a tcp client, handling astm message in a independent thread.
    """
    #def __init__(self, host_address='localhost', port='9000'):
    def __init__(self):
        self.message_sending_buffer = []
        self.host_address = 'localhost'
        self.port = '9999'
        self.load_communication_parameters_from_config_file()
        self.tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        self.connect()
        # start message handling in another thread.
        handler_thread = threading.Thread(target=self.handle_message_forever)
        handler_thread.setDaemon(True)
        handler_thread.start()

    def load_communication_parameters_from_config_file(self):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(PARAMETER_INI_FILE)
        if config_parser.has_section(COMMUNICATION_SECTION_NAME):
            self.host_address = config_parser.get(COMMUNICATION_SECTION_NAME,HOST_ADDRESS)
            self.port = config_parser.getint(COMMUNICATION_SECTION_NAME,CONNECT_PORT)

    def connect(self):
        try:
            self.tcp_client_socket.connect((self.host_address, int(self.port)))
        except Exception as e:
            project_logger.write_log_message(e)
            project_logger.write_log_message("connect to host:" + str(self.host_address) + "  port:" + str(self.port) + "  failed!")

    def close(self):
        self.tcp_client_socket.close()

    def message_handler(self):
        # message received handling
        received_message = self.tcp_client_socket.recv(RECEIVING_BUFFER_SIZE)
        print 'received message --- ', received_message
        if received_message:
            project_logger.write_log_message("message received: " + received_message)
            self.received_message_handler(received_message)
        # message to be sent handling
        # self.sending_message_handler()

    def received_message_handler(self, message):
        if ASTM_ENQ == message:
            print 'enq received...'
        elif ASTM_ACK == message:
            self.ack_handler()
        elif ASTM_EOT == message:
            print 'eot received...'
        else:
            print 'except characters received...'
            project_logger.write_log_message("except characters received... " + message)
            self.except_character_handler()

    def except_character_handler(self):
        message_to_be_sent = ASTM_NAK
        self.tcp_client_socket.send(message_to_be_sent)
        project_logger.write_log_message("message sent via ack_handler: " + message_to_be_sent)
        print  'message sent via ack_handler --- ', message_to_be_sent
        self.message_sending_buffer = []

    def ack_handler(self):
        if self.message_sending_buffer:
            # send the first message in the sending buffer and then remove it from the buffer.
            message_to_be_sent = self.message_sending_buffer.pop(0)
            self.tcp_client_socket.send(message_to_be_sent)
            time.sleep(0.1)
            project_logger.write_log_message("message sent via ack_handler: " + message_to_be_sent)
            print  'message sent via ack_handler --- ', message_to_be_sent
            if ASTM_EOT == message_to_be_sent:
                # check if next message should be sent.
                time.sleep(0.5)
                self.ack_handler()


    def trigger_a_sending(self):
        if len(self.message_sending_buffer) < 7 and self.message_sending_buffer[0] == ASTM_ENQ:
            self.tcp_client_socket.send(self.message_sending_buffer.pop(0))
            project_logger.write_log_message("message sent via trigger: " + ASTM_ENQ)
            print  'message sent via trigger --- <ENQ>'
            time.sleep(0.1)


    def push_enq_into_sending_buffer(self):
        self.message_sending_buffer.append(ASTM_ENQ)

    def push_header_message_into_sending_buffer(self):
        # <STX>1H|\^&|129584||CENTRALINK||Flexlab 3.6 November 1|||CENTRALINK 15.0.3||P|1|<CR><ETX>B2<CR>
        self.message_sending_buffer.append(str(ASTM_STX) + "1H|" +
            "\\" + "^&|129584||CENTRALINK||Flexlab 3.6 November 1|||CENTRALINK 15.0.3||P|1|" +
            ASTM_CR + ASTM_ETX + "B2" + ASTM_CR + ASTM_LF)

    def push_terminal_message_into_sending_buffer(self):
        # <STX>3L|1|N<CR><ETX>06<CR><LR>
        terminal_message = str(ASTM_STX) + "3L|1|N" + ASTM_CR + ASTM_ETX + "06" + ASTM_CR + ASTM_LF
        self.message_sending_buffer.append(terminal_message)

    def push_eot_into_sending_buffer(self):
        self.message_sending_buffer.append(ASTM_EOT)

    def construct_s004_by_sample_id_and_flag(self, sample_flag_info):
        message = ""
        sample_descriptio = ""
        if sample_flag_info.Description:
            sample_descriptio = '-' + str(sample_flag_info.Description)
        if isinstance(sample_flag_info, SampleFlagInfo):
            # <STX>2C|1|I|S004^0102666795\U09\10\Sampling Not Successful\20150828093637|S<CR><ETX>C2<CR><LF>
            message = "2C|1|I|S004^" + str(sample_flag_info.sample_id) + sample_descriptio + "\\" + str(sample_flag_info.flag) + "\\" + "01" + "\\" +\
                    str(sample_flag_info.Description) + "\\" + str(sample_flag_info.time_stamp) + "|S" + ASTM_CR + ASTM_ETX
            check_sum = self.make_message_check_sum(message)
            message = ASTM_STX + message
            message += check_sum + ASTM_CR + ASTM_LF
        return message

    def push_s004_message(self, sample_flag_info):
        message = self.construct_s004_by_sample_id_and_flag(sample_flag_info)
        self.message_sending_buffer.append(message)

    def send_sample_las_flag(self, sample_flag_info):
        self.push_enq_into_sending_buffer()
        self.push_header_message_into_sending_buffer()
        if isinstance(sample_flag_info, SampleFlagInfo):
            self.push_s004_message(sample_flag_info)
        self.push_terminal_message_into_sending_buffer()
        self.push_eot_into_sending_buffer()

        #if current sending buffer is empty, trigger a sending.
        self.trigger_a_sending()

    def send_sample_inlabbing_position_info(self, sample_position):
        if isinstance(sample_position, SampleInlabbingPosition):
            # enq
            self.push_enq_into_sending_buffer()
            # 1. astm head
            # <STX>1H|\^&|129584||CENTRALINK||Flexlab 3.6 November 1|||CENTRALINK 15.0.3||P|1|<CR><ETX>B2<CR>
            self.push_header_message_into_sending_buffer()
            # 2. sample position S001 message.
            # <STX>2C|1|I|S001^<sample id>\<node id>\<rack id>\<floor>\<lane id>\<rack position>\20151221115451|S<CR><STX>33<CR>
            # <STX>2C|1|I|S001^8005707319\01\024359\00\06\12\20151221115948|S<CR><ETX>3F<CR>
            sample_position_message = self.construct_s001_message_by_sample_position_info(sample_position)
            message_check_sum = self.make_message_check_sum(sample_position_message)
            sample_position_message += message_check_sum
            sample_position_message = str(ASTM_STX) + sample_position_message
            sample_position_message += ASTM_CR + ASTM_LF
            self.message_sending_buffer.append(sample_position_message)
            # 3. terminal message
            self.push_terminal_message_into_sending_buffer()
            # eot
            self.push_eot_into_sending_buffer()

    def construct_s001_message_by_sample_position_info(self, sample_position):
        if isinstance(sample_position, SampleInlabbingPosition):
            message = "2C|1|I|S001^" + str(sample_position.sample_id) + "\\01\\" +  str(sample_position.rack_id) +\
                "\\00\\" + str(sample_position.lane_id) + "\\" + str(sample_position.rack_position) +\
                "\\" + str(sample_position.time_stamp) + "|S" + ASTM_CR + ASTM_ETX
            return message

    @staticmethod
    def make_message_check_sum(message):
        checksum = 0
        for char in message:
            checksum += ord(char)
        checksum = str(hex(checksum))[-2:]
        return str(checksum).upper()


    def sending_message_handler(self):
        pass

    def send_method_enable_disable_message(self):
        pass

    def handle_message_forever(self):
        while True:
            self.message_handler()


class AstmThreadedClientManager():
    '''
    the interface to get threaded astm client.
    '''
    astm_client = AstmThreadedClient()

    @classmethod
    def get_astm_client(cls):
        return cls.astm_client

if __name__ == "__main__":
    aptio2_tranmit_client = AstmThreadedClient(host_address=' 172.22.27.147', port='9002')
    position1 = SampleInlabbingPosition(123456, 1, 2333, 12, 23, 20151221115948)
    position2 = SampleInlabbingPosition(33445566, 2, 2344, 12, 43, 20160128135311)
    aptio2_tranmit_client.send_sample_inlabbing_position_info(position1)
    aptio2_tranmit_client.send_sample_inlabbing_position_info(position2)
    aptio2_tranmit_client.trigger_a_sending()
