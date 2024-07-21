# Borg Backup Monitoring for Xymon

This project provides a monitoring solution for Borg backups within the Xymon monitoring framework. It consists of a Python script that parses Borg backup logs in JSON format and a cron script that checks the Borg backup status every 3 hours.

## Components

- `borgbackup.py`: A Python script that analyzes the Borg backup log, assesses backup health, and reports it to Xymon.
- `borg_xymon_cron_script.sh`: A shell script scheduled by cron to trigger the Python script at regular intervals.
- Configuration files for setting up the environment variables required by the scripts.

## Setup

### Dependencies

- Python 3
- BorgBackup (duh!)
- Xymon python lib 

### Installation
 - Clone the repository containing the monitoring scripts to your local system or server where you intend to run the monitoring.
   ```bash
   git clone https://example.com/borg-xymon-monitoring.git
   cd borg-xymon-monitoring
   ```
 - Run `pip install -r requirements.txt` to get xymon lib 
 - Copy file [borgbackup.py](borgbackup.py) to `xymon/client/ext/` exact path may vary depending on your xymon installation. For ubuntu its `/usr/lib/xymon/client/ext/borgbackup.py`
 - Copy file [borg_xymon_cron_script.sh](borg_xymon_cron_script.sh) to `/usr/local/bin/` or any other location you prefer.
 - Copy file [borg_config.sh](borg_config.sh) to `/usr/local/etc/borg.sh` or any other location you prefer.
 - Copy file [10-borgbackup.cfg](10-borgbackup.cfg) to `xymon/client/etc/clientlaunch.d` exact path may vary depending on your xymon installation. For ubuntu its `/usr/lib/xymon/client/etc/clientlaunch.d/10-borgbackup.cfg`
### Configuration

1.**Script Configuration**:
    - Modify `borg_config.sh` to include your Borg repository and passphrase.
    - Adjust the `yellow_time` and `red_time` parameters in `borgbackup.py` to match your backup frequency and tolerance for backup age.

2.**Cron Job Setup**:
    - Schedule `borg_xymon_cron_script.sh` to run at your desired frequency. For me its every 3h so I have added the following line to my crontab:
    ```bash 
    7 */3 * * * /usr/local/bin/borg_xymon_cron_script.sh
    ```
    - To change the frequency, edit the crontab entry for your user or the system.

### Log File and Directory Setup

- The default log file location for the Python script is `/var/log/local_backups/borg_backup.json`. Create this directory if it does not exist, or adjust the `borg_log_file` variable in `borgbackup.py` as needed.
- Ensure the log file and directory are writable by the user or process executing the scripts.

## Usage

Once configured, the system will automatically monitor Borg backups and report their status to Xymon. The status colors are as follows:

- **Green**: Backup is recent and within the defined `yellow_time`.
- **Yellow**: Backup is older than `yellow_time` but younger than `red_time`.
- **Red**: Backup is older than `red_time`, indicating a potential issue.

## Customization

Users may wish to adjust the following to suit their environment:

- **Backup Frequency**: Modify `yellow_time` and `red_time` in `borgbackup.py` to reflect your backup schedule.
- **Log Location**: Change the log file path in `borgbackup.py` if the default does not fit your setup.
- **Cron Frequency**: Edit the cron job setup to change how often the backup status is checked.

## Troubleshooting

Ensure all paths and environment variables are correctly set. Check the log files for errors if the system is not reporting as expected.

## Contributing

Contributions to improve the script or documentation are welcome. Please submit a pull request or open an issue for discussion.

## Acknowledgements

simple but very fine xymon library -> https://github.com/skurfer/python-xymon