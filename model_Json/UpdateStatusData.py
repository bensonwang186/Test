import json

class UpdateStatusData():
    def __init__(self, json_data):
        self._show_dialog = None
        self._check_data = None
        self._update_list = None
        self._last_version = None
        self._backup_exist = None

        if json_data:
            self.__dict__ = json.loads(json_data)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @property
    def show_dialog(self):
        return self._show_dialog

    @show_dialog.setter
    def show_dialog(self, value):
        self._show_dialog = value

    @property
    def check_data(self):
        return self._check_data

    @check_data.setter
    def check_data(self, value):
        self._check_data = value

    @property
    def update_list(self):
        return self._update_list

    @update_list.setter
    def update_list(self, value):
        self._update_list = value

    @property
    def last_version(self):
        return self._last_version

    @last_version.setter
    def last_version(self, value):
        self._last_version = value

    @property
    def backup_exist(self):
        return self._backup_exist

    @backup_exist.setter
    def backup_exist(self, value):
        self._backup_exist = value