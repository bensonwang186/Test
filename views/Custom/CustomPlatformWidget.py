import platform
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QSizePolicy

class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent)

        if platform.system() == 'Windows':
            pass
        elif platform.system() == 'Darwin': # cutsomize QComboBox to avoid MacOS native combobox style.
            self.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            #self.view().setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            self.view().setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
