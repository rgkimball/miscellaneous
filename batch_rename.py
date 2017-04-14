#!/usr/bin/python3

# rgkimball, 2017
# kimball.r@me.com

import csv
import os
from os import walk
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


class BatchRename:

    def __init__(self):
        self.today = datetime.now()

        # Pre-define class vars
        self.map_path = ""
        self.parent_path = ""
        self.flist = []
        self.file_map = ""
        self.failed = []
        self.success = 0

    def run(self):
        # Define & instantiate tkinter for file browsing
        root = tk.Tk()
        root.withdraw()

        print("Running the batch file renaming script. When prompted, please select the CSV file that contains the file name map.")
        print("The table should contain two columns, including file extension (i.e. 'MyFile.pdf'): Old Name, New Name.")
        input("Press enter to continue...")
        self.file_map = self.open_csv()

        while len(self.file_map) <= 0:
            print("Map CSV file was empty, please try a different file.")
            self.file_map = self.open_csv()

        print("Opened map file %s successfully, renaming %d file(s)." % (self.map_path, len(self.file_map)))

        print("When prompted, please select the folder containing all files that need to be renamed.")
        input("Press enter to continue...")
        self.open_folder()

        for (dirpath, dirnames, filenames) in walk(self.parent_path):
            self.flist.extend(filenames)
            break

        print("Found %d total file(s) in folder %s. Parsing for matches in map..." % (len(self.flist), self.parent_path))

        num = self.map_matches(False)

        if num > 0:
            input("Found matches, preparing to rename %d file(s). Press Enter to continue or Ctrl+C to exit." % num)
        else:
            print("No matches found. Please run script again with a different map or folder.")
            exit(1)

        self.map_matches(True)

        print("Script finished, renamed %d files, %d files failed." % (self.success, len(self.failed)))

        if len(self.failed) > 0:
            failed_list_file_path = os.path.join(dirpath, self.today.strftime("%Y%m%d") + "_failed.csv")

            with open(failed_list_file_path, "w", newline='', encoding='utf8') as csvfile:
                failedlist = csv.writer(csvfile, delimiter=',', quotechar='|')
                for row in self.failed:
                    failedlist.writerow([row])

    def open_folder(self):
        # File browsing prompt:
        self.parent_path = filedialog.askdirectory()

    def open_csv(self):
        # File browsing prompt:
        self.map_path = filedialog.askopenfilename()

        # Attempt to parse file
        with open(self.map_path, 'rt') as f:
            reader = csv.reader(f)
            return list(reader)

    def map_matches(self, run=False):
        num = 0
        rlist = {}
        for item in self.file_map:
            old_nam = item[0]
            if old_nam in self.flist:
                rlist[old_nam] = item[1]
                num += 1

        if run:
            for item in rlist:
                new_nam = rlist[item]

                # Replace any invalid characters to prevent errors:
                item = self.replace_invalid_chars(item)
                new_nam = self.replace_invalid_chars(new_nam)

                thisoldpath = os.path.join(self.parent_path, item)
                thisnewpath = os.path.join(self.parent_path, new_nam)

                try:
                    os.rename(thisoldpath, thisnewpath)
                    self.success += 1

                except FileNotFoundError:
                    self.failed.append(item)
                    continue
        else:
            return num

    @staticmethod
    def replace_invalid_chars(this):
        # Defines a map of characters that are invalid in Windows file name paths.
        invalid_map = {
            '<': '-',
            '>': '-',
            ':': '.',
            '/': '-',
            '\\': '-',
            '|': '--',
            '?': '.',
            '*': '.'
        }
        string = this
        for pattern in invalid_map:
            string = string.replace(pattern, invalid_map[pattern])
        return string

if __name__ == "__main__":
    br = BatchRename()
    br.run()
