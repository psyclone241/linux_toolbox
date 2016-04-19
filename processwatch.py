#!/usr/bin/env python
import ConfigParser
import traceback
import os
import psutil
import datetime
import time
import sqlite3 as db
import getpass
import json

class ProcessWatch:
    def __init__(self):
        self.config_data = None

        self.database_connection = None
        self.database_cursor = None
        self.process_list = None
        self.stored_process_list = {}
        self.scorecard = []
        self.limits = {
            'max_in_list': {
                'high': 50,
                'low': 1
            },
            'cpu_percent_interval': {
                'high': 5,
                'low': .01
            }
        }
        self.defaults = {
            'max_in_list': 5,
            'cpu_percent_interval': .25,
            'database_file': 'processwatch.db'
        }

        try:
            config = ConfigParser.ConfigParser()
            if os.path.exists('config.ini'):
                config.read("config.ini")
                self.config_data = {}
                self.config_data['database_file'] = config.get('GeneralSettings', 'DatabaseFile')
                self.config_data['max_in_list'] = config.get('GeneralSettings', 'MaxInList')
                self.config_data['cpu_percent_interval'] = config.get('GeneralSettings', 'CPUPercentInterval')
            else:
                raise Exception('No config.ini file was found')
        except Exception, e:
            print('Could not load config.ini')
            print(e)
        finally:
            # Define variables for use later in the class

            # If the config file was loaded, load settings, but use defaults
            # and limits for these 3 settings
            if self.config_data:
                if self.config_data['max_in_list']:
                    # Convert the configured value to int
                    self.max_in_list = int(self.config_data['max_in_list'])

                    # Allow between self.limits['max_in_list']['low'] and self.limits['max_in_list']['high']
                    # in the top X list of processes
                    if self.max_in_list < self.limits['max_in_list']['low'] or self.max_in_list > self.limits['max_in_list']['high']:
                        self.max_in_list = self.defaults['max_in_list']

                if self.config_data['cpu_percent_interval']:
                    # Convert the configured value to a float
                    self.cpu_percent_interval = float(self.config_data['cpu_percent_interval'])

                    # Allow between self.limits['cpu_percent_interval']['low'] and self.limits['cpu_percent_interval']['high']
                    if self.cpu_percent_interval < self.limits['cpu_percent_interval']['low'] or self.cpu_percent_interval > self.limits['cpu_percent_interval']['high']:
                        self.cpu_percent_interval = self.defaults['cpu_percent_interval']

                if self.config_data['database_file']:
                    self.database_file = self.config_data['database_file']
            else:
                # Default to a top 5 list
                # Default to a quarter second interval of refresh (used for CPU %)
                # Default to processwatch.db
                self.max_in_list = self.defaults['max_in_list']
                self.cpu_percent_interval = self.defaults['cpu_percent_interval']
                self.database_file = self.defaults['database_file']


            # Formatting that is not configurable and set here so that it might
            # be configured later if need be
            self.process_table = 'processwatch'
            self.create_table_columns = '(id INTEGER PRIMARY KEY, rss BIGINT, cpu_percent BIGINT, pid INT, ppid INT, username TEXT, name TEXT, cmdline TEXT, rank INT, create_time TEXT, run_as TEXT, timestamp TEXT)'
            self.abs_round_memory_format = '%3.1f%s%s'
            self.other_round_memory_format = '%.1f%s%s'
            self.timestamp_format = '%Y-%m-%d %H:%M:%S'
            self.display_column_format = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'
            self.display_pid_justification = 6
            self.display_user_justification = 15
            self.display_name_justification = 20
            self.display_rsscpu_justification = 10

    def main(self):
        self.databaseSetup()
        self.getProcessList()
        self.readProcessList()
        self.scoreProcessList()

    def sizeof_fmt(self, num, suffix='b'):
        try:
            for unit in ['','k','m','g','t','p','e','z']:
                if abs(num) < 1024.0:
                    return self.abs_round_memory_format % (num, unit, suffix)
                num /= 1024.0
            return self.other_round_memory_format % (num, 'y', suffix)
        except:
            return 0

    def databaseSetup(self):
        # Check for a database containing a table called 'traffic_data'
        try:
            self.database_connection = db.connect(self.database_file)
            self.database_cursor = self.database_connection.cursor()
            self.database_cursor.execute('SELECT * from ' + self.process_table)
            process_data = self.database_cursor.fetchall()
        except db.Error, e:
            error_message = e.args[0]

            if 'no such table' in error_message:
                print('No process data storage table in DB, creating table "' + self.process_table + '"')
                try:
                    self.database_cursor.execute('CREATE TABLE ' + self.process_table + ' ' + self.create_table_columns)
                    self.database_cursor.execute('SELECT * from ' + self.process_table)
                    process_data = self.database_cursor.fetchall()
                except db.Error, e:
                    error_message = e.args[0]
                    print "Error in DB: %s" % error_message
                    exit()
            else:
                print "Error in DB: %s" % error_message
                exit()
        finally:
            if self.database_connection:
                self.database_connection.close()

    def getProcessList(self):
        self.process_list = psutil.process_iter()

    def readProcessList(self):
        if self.process_list:
            for process in self.process_list:
                try:
                    pinfo = process.as_dict(attrs=['pid', 'name', 'memory_info'])
                except psutil.NoSuchProcess:
                    pass
                else:
                    # create_time = datetime.datetime.fromtimestamp(pinfo['create_time']).strftime(self.timestamp_format)
                    pid = pinfo['pid']
                    name = pinfo['name']
                    if 'memory_info' in pinfo:
                        if pinfo['memory_info']:
                            self.scorecard.append((pinfo['pid'], pinfo['name'], pinfo['memory_info'][0]))
        else:
            print('No processes were collected')

    def scoreProcessList(self):

        self.database_connection = db.connect(self.database_file, isolation_level=None)
        self.database_cursor = self.database_connection.cursor()

        # Setup the columns for printing on screen results
        print(self.display_column_format % ('Rank', 'PID'.ljust(self.display_pid_justification), 'PPID'.ljust(self.display_pid_justification), 'CUser'.ljust(self.display_user_justification), 'PUser'.ljust(self.display_user_justification), 'Name'.ljust(self.display_name_justification), 'RSS'.ljust(self.display_rsscpu_justification), 'CPU%'.ljust(self.display_rsscpu_justification)))

        # Sort the scorecards from the readProcessList returned value
        self.scorecard = sorted(self.scorecard, key=lambda x: x[2], reverse=True)

        # Start the ranking at 1, because it would be silly not to
        rank = 1
        # Set a single timestamp for each run that is stored in the database
        timestamp = time.time()
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime(self.timestamp_format)

        # Leave this loop open so that we could in theory handle things outside
        # of the max_in_list variable set in configuration
        for process in self.scorecard:
            if rank <= self.max_in_list:
                pid = process[0]
                name = process[1]
                rss = process[2]

                try:
                    # First get the details of the process directly from the system
                    process_info = psutil.Process(pid)
                    process_info = process_info.as_dict()
                    process_user = process_info['username']
                    ppid = process_info['ppid']
                    command_line = json.dumps(process_info['cmdline'])
                    create_time = datetime.datetime.fromtimestamp(process_info['create_time']).strftime(self.timestamp_format)

                    # Independently grab the process a second time so as to get
                    # an accurate reading of the CPU%
                    # Read -> https://pythonhosted.org/psutil/#psutil.Process.cpu_percent
                    process_info = psutil.Process(pid)
                    cpu_percent = process_info.cpu_percent(interval=self.cpu_percent_interval)
                    current_user = getpass.getuser()

                    # Print each row of data
                    print(self.display_column_format % (str(rank), str(pid).ljust(self.display_pid_justification), str(ppid).ljust(self.display_pid_justification), current_user.ljust(self.display_user_justification), process_user.ljust(self.display_user_justification), name.ljust(self.display_name_justification), str(self.sizeof_fmt(rss)).ljust(self.display_rsscpu_justification), str(cpu_percent).ljust(self.display_rsscpu_justification)))

                    # Run an insert query to store this row in the database
                    data = (rank, pid, ppid, current_user, process_user, name, rss, cpu_percent, command_line, timestamp, create_time)
                    self.database_cursor.execute("INSERT INTO " + self.process_table + "(rank, pid, ppid, run_as, username, name, rss, cpu_percent, cmdline, timestamp, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
                except psutil.NoSuchProcess:
                    pass

            # Increment the ranking variable by one
            # This is used to mark the record in the database with a score
            # for use in determining the processes rank at the time of the test
            rank += 1

        self.database_connection.close()

debug = True
if __name__ == '__main__':
    try:
        thisapp = ProcessWatch()
        thisapp.main()
    except Exception as main_run_exception:
        if debug:
            print('__main__: ' + str(main_run_exception))
            print(traceback.format_exc())
        else:
            # TODO: Add logging to the application
            print('We encountered an error, please look at the log file')
    except KeyboardInterrupt:
        pass
