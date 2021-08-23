import traceback

from PyQt5.QtCore import pyqtSignal, QObject

from major import Command
from Utility import Logger
from model_Json.UpdateStatusData import UpdateStatusData


class SoftwareUpdateHandler(QObject):
    def __init__(self, about_page, client):
        super(SoftwareUpdateHandler, self).__init__()
        self.about_page = about_page
        self.client = client
        self.about_page.check_update_signal.connect(self.check_update_slot)
        self.about_page.run_update_signal.connect(self.run_update_slot)
        self.about_page.run_restore_signal.connect(self.run_restore_slot)

        self.client.update_status_signal.connect(self.update_status_slot)
        self.client.update_dialog_result_signal.connect(self.update_dialog_result_slot)

    def check_update_slot(self):
        self.client.queryRequest(Command.TARGET_CHECK_UPDATE, "")

    def run_update_slot(self, data):
        self.client.queryRequest(Command.TARGET_SOFTWARE_UPDATE, data)

    def run_restore_slot(self, data):
        self.client.queryRequest(Command.TARGET_SOFTWARE_RESTORE, "")

    def update_status_slot(self, data):
        temp = data.param
        model = UpdateStatusData(temp)
        self.about_page.check_update_result(model)

    def update_dialog_result_slot(self, type):
        self.about_page.software_update_dialog_result(type)

