from .AptioSystemReagent import Ui_Aptio_System_Reagent
from .Aptio_Reagent_Info import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class AptioSystemReagentDialog(QDialog):
    def __init__(self, aptio_reagent_info=None, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_Aptio_System_Reagent()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowMinimizeButtonHint)

        self.ui.treeWidget.setColumnCount(2)
        self.ui.treeWidget.setHeaderLabels(['Instrument','Reagent'])
        #self.update_reagent_tree(aptio_reagent_info)

    '''
    def __del__(self):
        self.emit('window_closed()')
    '''

    def update_reagent_tree(self,aptio_reagent_info=None):
        #init the tree widget to display aptio system reagent status.
        self.ui.treeWidget.clear()

        if aptio_reagent_info <> None and isinstance(aptio_reagent_info,AptioReagentInfo):
            aptio = QTreeWidgetItem(self.ui.treeWidget)
            aptio.setText(0,'Aptio')
            AptioSystemReagentDialog.update_item_background_color(aptio,aptio_reagent_info.reagent_status)
            for instrument_item in aptio_reagent_info.reagent_info_table:
                if isinstance(instrument_item,InstrumentReagentInfo):
                    instr_node = QTreeWidgetItem(aptio)
                    instr_node.setText(0,str(instrument_item.instrument_name))
                    AptioSystemReagentDialog.update_item_background_color(instr_node,instrument_item.reagent_status)
                    for reagent_item in instrument_item.reagent_info_list:
                        if isinstance(reagent_item,ReagentInfoItem):
                            reagent_node = QTreeWidgetItem(instr_node)
                            reagent_node.setText(1,reagent_item.reagent_name + ": " + str(reagent_item.reagent_count))
                            AptioSystemReagentDialog.update_item_background_color(reagent_node,reagent_item.reagent_status)

        #self.ui.treeWidget.expandAll()


    @staticmethod
    def update_item_background_color(item,reagent_status):
        if reagent_status == RED:
            item.setBackgroundColor(0,QColor(255,0,0))
        elif reagent_status == YELLOW:
            item.setBackgroundColor(0,QColor(255,255,0))
        else:
            item.setBackgroundColor(1,QColor(0,255,0))
