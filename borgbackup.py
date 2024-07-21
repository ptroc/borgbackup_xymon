#!/usr/bin/env python3
# file location: /usr/lib/xymon/client/ext/borgbackup.py
import datetime
import json
import logging
import os

from xymon import Xymon


class xymon_borg_backup:
    def __init__(self, hostname: str, service: str,
                 yellow_time: int, red_time: int, log_file: str, log_level: int = logging.INFO):
        self.yellow_time = yellow_time
        self.red_time = red_time
        self.log_file = log_file
        self.log_level = log_level
        self.logger = logging
        self.hostname = hostname
        self.service = service
        self.server = Xymon()
        self.logger.basicConfig(
            format='[%(asctime)s] %(levelname)s %(process)d --- [%(threadName)s] %(funcName)s: %(message)s',
            level=self.log_level
        )
        # check if file exists
        try:
            with open(self.log_file, 'r') as f:
                pass
        except FileNotFoundError:
            self.logger.error(f"File {self.log_file} not found.")
            exit(1)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            exit(1)

    def check_borg_backup(self):
        self.logger.info(f"Checking Borg Backup status, using file {self.log_file}")
        borg_json_data = self._get_json_data()
        if not "archives" in borg_json_data:
            self.logger.error("No archives found in json file")
            self._send_red_status(f"Invalid json file found at {self.log_file}")
        last_archive = borg_json_data["archives"].pop()
        last_archive_start_time = last_archive["start"]

        if not last_archive_start_time:
            self.logger.error("No start time found in json file")
            self._send_red_status(f"Invalid json file found at {self.log_file}")
        # convert 2022-12-22T00:00:04.000000 date format to python datetime object
        last_archive_start_time = datetime.datetime.strptime(last_archive_start_time, "%Y-%m-%dT%H:%M:%S.%f")
        # calculate duration of last backup betwen start and end time
        last_archive_end_time = datetime.datetime.strptime(last_archive['end'], "%Y-%m-%dT%H:%M:%S.%f")
        last_archive['duration'] =  last_archive_end_time - last_archive_start_time
        if last_archive_start_time < datetime.datetime.now() - datetime.timedelta(hours=self.red_time):
            self.logger.error(
                f"Last archive start time: {last_archive_start_time}, archive name: {last_archive['name']}")
            self._send_red_status(
                f"Last archive start time: {last_archive_start_time}\nArchive name: {last_archive['name']}\n"
                f"Age of last archive: {datetime.datetime.now() - last_archive_start_time}\n"
                f"Duration of last backup: {last_archive['duration']}")
        elif last_archive_start_time < datetime.datetime.now() - datetime.timedelta(hours=self.yellow_time):
            self.logger.warning(
                f"Last archive start time: {last_archive_start_time}, archive name: {last_archive['name']}")
            self._send_yellow_status(
                f"Last archive start time: {last_archive_start_time}\nArchive name: {last_archive['name']}\n"
                f"Age of last archive: {datetime.datetime.now() - last_archive_start_time}\n"
                f"Duration of last backup: {last_archive['duration']}")
        else:
            self.logger.info(
                f"Last archive start time: {last_archive_start_time}, archive name: {last_archive['name']}")
            self._send_green_status(
                f"Last archive start time: {last_archive_start_time}\nArchive name: {last_archive['name']}\n"
                f"Age of last archive: {datetime.datetime.now() - last_archive_start_time}\n"
                f"Duration of last backup: {last_archive['duration']}")

    def _get_json_data(self):
        with open(self.log_file) as f:
            d = json.load(f)
        return d

    def _extra_info(self):
        msg = (
            f"Borg backup monitoring\nLog file: {self.log_file}\nNumber of backups: {len(self._get_json_data()['archives'])}\n"
            f"Last repository change: {self._get_json_data()['repository']['last_modified']}\n")
        return msg

    def _send_red_status(self, message):
        _message = f"{self._extra_info()}\n{message}"
        self.server.report(host=self.hostname, test=self.service, color="red", message=_message)

    def _send_yellow_status(self, message):
        _message = f"{self._extra_info()}\n{message}"
        self.server.report(host=self.hostname, test=self.service, color="yellow", message=_message)

    def _send_green_status(self, message):
        _message = f"{self._extra_info()}\n{message}"
        self.server.report(host=self.hostname, test=self.service, color="green", message=_message)


if __name__ == "__main__":
    # get $MACHINE bash environment variable
    borg_log_file = "/var/log/local_backups/borg_backup.json"
    xymon = xymon_borg_backup(hostname=os.getenv("MACHINE"), service="borg_backup", yellow_time=30, red_time=60,
                              log_file=borg_log_file)
    xymon.check_borg_backup()