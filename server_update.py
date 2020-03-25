import tempfile
import urllib.request
from urllib.error import URLError
import os
import shutil
import json
import sys
from math import ceil
import traceback
import argparse

"""
A Set of tools to automate the server update process.
Error philosophy:
 > As long as it is LOGGED or DISPLAYED somewhere for the user to see, it has been handled.
 """


def error_report(exc, net=False):

    """
    Function for displaying error information to the terminal
    :param exc: Exception object
    :param net: Weather to include network information
    :return:
    """

    print("+==================================================+")
    print("  [ --== The Following Error Has Occurred: ==-- ]")
    print("+==================================================+")

    # Print error name

    print("Error Name: {}".format(exc))
    print("+==================================================+")

    # Print full traceback:

    print("Full Traceback:")
    traceback.print_exc()
    print("+==================================================+")

    if net:

        # Include extra network information

        print("Extra Network Information:")

        if hasattr(exc, 'reason'):

            print("We failed to reach the server.")
            print("Reason: {}".format(exc.reason))

        if hasattr(exc, 'code'):

            print("The server could not fulfill the request.")
            print("Error code: {}".format(exc.code))

    print("+==================================================+")
    print("(Can you make anything of this?)")
    print("Please check the github page for more info: https://github.com/Owen-Cochell/PaperMC-Update.")

    input("Press enter to continue...")

    return


class Update:

    """
    Server updater, handles checking, downloading, and installing.
    """

    def __init__(self, ver):

        self.ver = ver  # Version of the minecraft server we are currently using.
        self._base = 'https://papermc.io/api/v1/paper'  # Base URL to build of off
        self._headers = {
             'Content-Type': 'application/json;charset=UTF-8',
             'Accept': 'application/json, text/plain, */*',
             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:43.0) Gecko/20100101 Firefox/43.0',
             'Accept-Language': 'en-US,en;q=0.5',
             'DNT': '1',
         }  # Request headers for contacting Paper Download API, emulating a Google client

    def _progress_bar(self, total, step, end, prefix="", size=60, prog_char="#", empty_char="."):

        """
        Outputs a simple progress bar to stdout
        :param total: Total amount of computations
        :param step: Amount to increase the counter by
        :param end:  Number to end on
        :param prefix: What to show before the progress bar
        :param size: Size of the progress bar
        :return:
        """

        # Iterating over the total number of iterations:

        for i in range(total):

            # Yield i

            yield i

            # Calculate number of '#' to render:

            x = int(size*(i+1)/total)

            # Rendering progress bar:

            sys.stdout.write("{}[{}{}] {}/{}\r".format(prefix, prog_char*x, empty_char*(size-x),
                                                       (i*step if i < total - 1 else end), end))
            sys.stdout.flush()

        # Writing newline, to continue execution

        sys.stdout.write("\n")
        sys.stdout.flush()

    def _url_report(self, point):

        """
        Reports an error during a request operation
        :param point: Point of failure
        :return:
        """

        print("\n+==================================================+")
        print("> !ATTENTION! >")
        print("An error occurred during a request operation.")
        print("Fail Point: {}".format(point))
        print("Your check/update operation will be canceled.")
        print("Detailed error info below:")

    def download(self, path, version, build_num='latest'):

        """
        Gets file from Paper API, and displays a progress bar
        Write to the file specified in chunks, as to not fill up or memory
        :param version: Version to download
        :param build_num: Build to download
        :param path: Path to file to write to
        :return: True on success, False on Failure
        """

        print("\n[ --== Starting Download: ==-- ]")

        # Building URL here:

        url = self._base + '/' + str(version) + '/' + str(build_num) + '/download'

        print("URL: {}".format(url))

        # Creating request here:

        req = urllib.request.Request(url, headers=self._headers)

        # Sending request to Paper API

        try:

            data = urllib.request.urlopen(req)

        except URLError as e:

            self._url_report("File Download")

            # Network error occurred

            error_report(e, net=True)

            return False

        # Getting content length of download:

        length = int(data.getheader('content-length'))
        blocksize = 4608

        print("Download Size: {}".format(length))

        file = open(path, mode='ba')

        # Using progress bar to visualise download:

        try:

            for i in self._progress_bar(ceil(length/blocksize) + 1, blocksize, length, prefix='Downloading:'):

                # Getting blocksize data:

                byts = data.read(blocksize)

                # Writing data to file:

                file.write(byts)

        except URLError as e:

            self._url_report("File Download")

            # Report the error

            error_report(e, net=True)

            file.close()

            return False

        except Exception as e:

            self._url_report("File Download")

            # Report the error

            error_report(e)

            file.close()

            return False

        # Closing file:

        file.close()

        # Done downloading

        print("[ --== Download Complete! ==-- ]")

        return True

    def _get(self, version=None, build_num=None):

        """
        Gets RAW data from the Paper API, version info only
        :param version: Version to include in the URL
        :param build_num: Build number to include in the URL
        :return: urllib Request object
        """

        # Building url:

        final = self._base

        if version is not None:

            # Specific version requested:

            final = final + '/' + str(version)

            if build_num is not None:

                # Specific build num requested:

                final = final + '/' + str(build_num)

        # Creating request here:

        req = urllib.request.Request(final, headers=self._headers)

        # Getting data:

        try:

            data = urllib.request.urlopen(req)

        except Exception as e:

            self._url_report("API Fetch Operation")

            # Exception occurred, handel it

            error_report(e, net=True)

            return None

        return data

    def get_versions(self):

        """
        Gets available versions of the server
        :return: List of available versions
        """

        # Getting raw data and converting it to JSON format

        print("  > Fetching and decoding version info...")

        data = self._get()

        if data is None:

            # Error occurred

            return None

        data = json.loads(data.read())

        # Returning version info

        print("  > Done fetching version information!")

        return data['versions']

    def get_buildnums(self, version):

        """
        Gets available build for a particular version
        :param version: Version to get builds for
        :return: List of builds
        """

        # Getting raw data and converting it to JSON format

        print("  > Fetching and decoding build info...")

        data = self._get(version=version)

        if data is None:

            # Error occurred

            return None

        data = json.loads(data.read())

        print("  > Done fetching build info!")

        return data['builds']['all']


class FileUtil:

    """
    Class for managing the creating/deleting/moving of server files
    """

    def __init__(self, path):

        self.path = path  # Path to file being updated
        self.temp = None  # Tempdir instance
        self._working_path = os.path.join(os.path.expanduser("~"), '.server_update')  # Working directory path

    def create_temp_dir(self):

        """
        Creates a temporary directory
        :return: Temp file instance
        """

        self.temp = tempfile.TemporaryDirectory()

        return self.temp

    def close_temp_dir(self):

        """
        Closes created temporary directory
        :return:
        """

        self.temp.close()

    def create_working_dir(self):

        """
        Creates working directory in the users home folder
        Checks if one exists already.
        :return:
        """

        # Checking if working directory exists

        if not os.path.isdir(self._working_path):

            # Creating directory

            os.mkdir(self._working_path, 0o755)

        return

    def cleanup_working_dir(self):

        """
        Cleanup and removes the current working directory
        :return:
        """

        # Checking if directory exists:

        print("# Cleaning working directory...")

        if os.path.isdir(self._working_path):

            # Removing directory

            shutil.rmtree(self._working_path)

        print("# Done cleaning working directory!")

        return

    def load_config(self):

        """
        Loads configuration info from config file
        :return:
        """

        print("# Loading configuration data...")

        if os.path.isfile(os.path.join(self._working_path, 'config.json')):

            # File exists, read data from it

            file = open(os.path.join(self._working_path, 'config.json'), 'r')

            config = json.loads(file.read())

            file.close()

            print("# Done loading configuration data!")

            return config['version'], config['build']

        # Could not find config file, return default vals

        print("# Could not find configuration file.")

        return '0', 0

    def dump_config(self, version, build):

        """
        Dumps configuration data to file
        :param version: Version server is on
        :param build: Build server is on
        :return:
        """

        print("# Dumping configuration data...")

        if not os.path.isdir(self._working_path):

            print("# Creating working directory[{}]".format(self._working_path))

            # Directory does not exist, creating

            self.create_working_dir()

            print("# Done creating working directory!")

        config = open(os.path.join(self._working_path, 'config.json'), 'w')

        config.write(json.dumps({'version': version, 'build': build}))

        config.close()

        print("# Done dumping configuration data!")

        return

    def _fail_install(self, point):

        """
        Shows where the error occurred during the instillation
        :param point: Point of failure
        :return:
        """

        print("\n+==================================================+")
        print("> !ATTENTION! <")
        print("A error occurred during the instillation, and we can not continue.")
        print("We will attempt to recover your previous instillation(If applicable)")
        print("Fail point: {}".format(point))
        print("Detailed error info below:")

        return

    def install(self):

        """
        "Installs" the contents of the temporary file into the target in the root server directory.
        :return:
        """

        print("\n[ --== Instillation: ==-- ]")

        # Creating backup of old file:

        print("# Creating backup of previous installation...")

        try:

            shutil.copyfile(self.path, os.path.join(self.temp.name, 'backup'))

        except Exception as e:

            # Show install error

            self._fail_install("File Backup")

            # Show error info

            error_report(e)

            return False

        print("# Backup created at: {}".format(os.path.join(self.temp.name, 'backup')))

        # Removing current file:

        print("# Deleting current file at {}...".format(self.path))

        try:

            os.remove(self.path)

        except Exception as e:

            self._fail_install("Old File Deletion")

            # Showing error

            error_report(e)

            # Recovering backup

            self._recover_backup()

            return False

        print("# Removed original file!")

        # Copying downloaded file to root:

        try:

            print("# Copying download data to root directory...")
            print("# ({} > {})".format(os.path.join(self.temp.name, 'download_data'),
                                       self.path))

            shutil.copyfile(os.path.join(self.temp.name, 'download_data'), self.path)

        except Exception as e:

            # Install error

            self._fail_install("File Copy")

            # Show error

            error_report(e)

            # Recover backup

            self._recover_backup()

            return False

        print("# Done copying download data to root directory!")

        # Cleaning up temporary directory:

        print("# Cleaning up temporary directory...")

        self.temp.cleanup()

        print("# Done cleaning temporary directory!")

        print("[ --== Instillation complete! ==-- ]")

        return True

    def _recover_backup(self):

        """
        Recovers the backup of the old server jar file
        :return:
        """

        print("+==================================================+")
        print("\n> !ATTENTION! <")
        print("A failure has occurred during the instillation process.")
        print("I'm sure you can see the error information above.")
        print("This script will attempt to recover your old instillation.")
        print("If this operation fails, check the github page for more info: https://github.com/Owen-Cochell/PaperMC-Update")

        # Deleting file in root directory:

        print("# Deleting Corrupted temporary File...")

        try:

            os.remove(self.path)

        except FileNotFoundError:

            # File was not found. Continuing...

            print("# File not found. Continuing operation...")

        except Exception as e:

            print("# Critical error during recovery process!")
            print("# Displaying error information:")

            error_report(e)

            print("Your previous instillation could not be recovered.")

            return False

        # Copying file to root directory:

        print("# Copying backup file[{}] to server root directory[{}]...".format(os.path.join(self.temp.name, 'backup'),
                                                                                 self.path))

        try:

            shutil.copyfile(os.path.join(self.temp.name, 'backup'), self.path)

        except Exception as e:

            print("# Critical error during recovery process!")
            print("# Displaying error information:")

            error_report(e)

            print("Your previous instillation could not be recovered.")

            return False

        print("\nRecovery process complete!")
        print("Your file has been successfully recovered.")
        print("Please debug the situation, and figure out why the problem occurred,")
        print("Before re-trying the update process.")

        return True


class ServerUpdater:

    """
    Class that binds all server updater classes together
    """

    def __init__(self, path, version=None, build=None, config=True, prompt=True):

        self.version = version  # Version of minecraft server we are running
        self.fileutil = FileUtil(path)  # Fileutility instance
        self.buildnum = build  # Buildnum of the current server
        self._available_versions = []  # List of available versions
        self.prompt = prompt  # Weather to prompt the user for version selection

        # Starting object

        self._start(config)

        self.update = Update(self.version)  # Updater Instance

    def _start(self, config):

        """
        Starts the object, loads configuration
        :return:
        """

        if config and self.version == 'NONE' and self.buildnum == 'NONE':

            # Allowed to use configuration file

            self.version, self.buildnum = self.fileutil.load_config()

        else:

            # Setting true default values

            print("# Skipping configuration file")

            self.version = (self.version if self.version != 'NONE' else '0')
            self.buildnum = (self.buildnum if self.buildnum != 'NONE' else 0)

        print("\nServer Version Information:")
        print("  > Version: [{}]".format(self.version))
        print("  > Build: [{}]".format(self.buildnum))

        return

    def check(self):

        """
        Checks if a new version is available
        :return: True is new version, False if not/error
        """

        print("\n[ --== Checking For New Version: ==-- ]")

        # Checking for new server version

        print("# Comparing local <> remote server versions...")

        ver = self.update.get_versions()

        if ver is None:

            # Error occurred

            return False

        if ver[0] != self.version:

            # New version available!

            print("# New Version available! - [Version: {}]".format(ver[0]))
            print("[ --== Version check complete! ==-- ]\n")

            return True

        print("> No new version available.")

        # Checking builds

        print("# Comparing local <> remote builds...")

        build = self.update.get_buildnums(self.version)

        if build is None:

            # Error occurred

            return False

        if build[0] != self.buildnum:

            # New build available!

            print("# New build available! - [Build: {}]".format(build[0]))
            print("[ --== Version check complete! ==-- ]\n")

            return True

        print("# No new versions found.")
        print("[ --== Version check complete! ==-- ]\n")

        return False

    def _select(self, val, choice, default, name):

        """
        Selects a value from the choices.
        Support updater keywords
        :param val: Value entered
        :param choice: Choices to choose from
        :param default: Default value
        :param name: Name of value we are choosing
        :return: True if valid, false if invalid
        """

        if val == '':

            # User wants default value:

            val = default


        if val == 'latest':

            # User wants latest

            print("# Selecting latest {} - [{}]...".format(name, self._available_versions[0]))

            val = choice[0]

            return True, val

        if val not in choice:

            # User selected invalid option

            print("\n# Error: Invalid {} selected!".format(name))

            return False, ''

        # Option selected is valid. Continue

        print("# Selecting {}: [{}]...".format(name, val))

        return True, val

    def version_select(self, default_version='latest', default_build='latest'):

        """
        Prompts the user to select a version to download
        Checks input against values from Paper API
        Default value is recommended values
        :param default_build: Default build number
        :param default_version: Default version
        :return: (version, build)
        """

        # Checking if we have version information:

        print("# Checking version information...")

        if not self._available_versions:

            # Version information is empty, reloading

            print("# Loading version information...")

            data = self.update.get_versions()

            if data is None:

                # Error occurred

                return None, None

            self._available_versions = data

        if self.prompt:

            print("\n[ --== Version Select: ==-- ] ")

            print("\nPlease enter the version you would like to download:")
            print("Example: 14.4.4")
            print("(Tip: The value enclosed in brackets is the default option. Leave the prompt blank to accept it.)")
            print("(Tip: Enter 'latest' to select the latest version.)")

            print("\nAvailable versions:")

            # Displaying available versions

            for i in self._available_versions:

                print("  > Version: [{}]".format(i))

            while True:

                ver = input("\nEnter Version[{}]: ".format(default_version))

                stat, ver = self._select(ver, self._available_versions, default_version, "version")

                if stat:

                    # User selected okay value

                    break

        else:

            # Just select default version

            stat, ver = self._select('', self._available_versions, default_version, "version")

            if not stat:

                # Invalid version selected

                print("# Aborting instillation!")

                return None, None

        # Getting build info

        print("# Loading build information...")

        nums = self.update.get_buildnums(ver)

        if nums is None:

            # Error occurred:

            return None, None

        if self.prompt:

            print("\nPlease enter the build you would like to download:")
            print("Example: 205")
            print("(Tip: The value enclosed in brackets is the default option. Leave the prompt blank to accept it.)")
            print("(Tip: Enter 'latest' to select the latest build.)")

            print("\nAvailable Builds:")

            # Displaying available builds

            for i in nums:

                print("  > Build Num: [{}]".format(i))

            while True:

                # Prompting user for build info

                build = input("\nEnter Build[{}]: ".format(default_build))

                stat, build = self._select(build, nums, default_build, "build")

                if stat:

                    # User selected okay value

                    break

        else:

            # Select default build

            stat, build = self._select('', nums, default_build, "build")

            if not stat:

                # Invalid build selected!

                print("# Aborting instillation!")

                return None, None

        print("\nYou have selected:")
        print("   > Version: [{}]".format(ver))
        print("   > Build: [{}]".format(build))

        print("\n[ --== Version Selection Complete! ==-- ]")

        return ver, build

    def get_new(self, default_version='latest', default_build='latest'):

        """
        Downloads and installs the new version
        Prompts the user to select a specific version
        :return:
        """

        # Prompting user for version info:

        ver, build = self.version_select(default_version=default_version, default_build=default_build)

        if ver is None or build is None:

            # Error occurred, cancel instillation

            return

        # Checking if user wants to continue with instillation

        if self.prompt:

            print("\nDo you want to continue with the instillation?")

            inp = input("(Y/N):").lower()

            if inp in ['n', 'no']:
                # User does not want to continue, exit

                print("Canceling instillation...")

                return

        # Creating temporary directory to store assets:

        print("# Creating temporary directory...")

        self.fileutil.create_temp_dir()

        print("# Temporary directory created at: {}".format(self.fileutil.temp.name))

        # Starting download process:

        val = self.update.download(os.path.join(self.fileutil.temp.name, 'download_data'), ver, build_num=build)

        if not val:

            # Download process failed

            return

        # Download process complete!

        # Installing downloaded data:

        val = self.fileutil.install()

        if not val:

            # Install process failed

            return

        print("\nUpdate complete!")

        # Updating values

        self.version = ver
        self.buildnum = build

        return


if __name__ == '__main__':

    # Ran as script

    print("+==========================================================================+")
    print("""|     _____                              __  __          __      __        |  
|    / ___/___  ______   _____  _____   / / / /___  ____/ /___ _/ /____    |
|    \__ \/ _ \/ ___/ | / / _ \/ ___/  / / / / __ \/ __  / __ `/ __/ _ \\   |
|   ___/ /  __/ /   | |/ /  __/ /     / /_/ / /_/ / /_/ / /_/ / /_/  __/   |
|  /____/\___/_/    |___/\___/_/      \____/ .___/\__,_/\__,_/\__/\___/    |
|                                         /_/                              |""")
    print("+==========================================================================+")
    print("\n[Minecraft Server Updater]")
    print("[Handles the checking, downloading, and instillation of server versions]")
    print("[Written by: Owen Cochell]\n")

    parser = argparse.ArgumentParser(description='Minecraft Server Updater.',
                                     epilog="Please check the github page for more info: https://github.com/Owen-Cochell/PaperMC-Update.")

    parser.add_argument('path', help='Path to file to be updated')
    parser.add_argument('-v', '--version', help='Server version to install(Sets default value)', default='latest')
    parser.add_argument('-b', '--build', help='Server build to install(Sets default value)',  default='latest')
    parser.add_argument('-iv', help='Sets the currently installed server version, ignores config', default='NONE')
    parser.add_argument('-ib', help='Sets the currently installed server build, ignores config.', default='NONE')
    parser.add_argument('-C', '--cleanup', help='Deletes config directory and all sub-files', action='store_true')
    parser.add_argument('-c', '--check-only', help='Checks for an update, does not install', action='store_true')
    parser.add_argument('-nc', '--no-check', help='Does not check for an update, skips to install', action='store_true')
    parser.add_argument('-i', '--interactive', help='Prompts the user for the version they would like to install.', action='store_true')
    parser.add_argument('-nlc', '--no-load-config', help='Will not load config information', action='store_false')
    parser.add_argument('-ndc', '--no-dump-config', help="Will not dump configuration information.", action='store_false')

    args = parser.parse_args()

    serv = ServerUpdater(args.path, config=args.no_load_config, prompt=args.interactive,
                         version=args.iv, build=args.ib)

    update_available = True

    # Checking if we are skipping the update

    if not args.no_check:

        # Allowed to check for update:

        update_available = serv.check()

    # Checking if we can install:

    if not args.check_only and update_available:

        # Allowed to install/Can install

        serv.get_new(default_version=args.version, default_build=args.build)

    # Checking if we can dump current configuration:

    if args.no_dump_config and not args.check_only:

        # We can dump our configuration data

        serv.fileutil.dump_config(serv.version, serv.buildnum)

    # Checking if we have to clean up:

    if args.cleanup:

        # Cleaning up

        serv.fileutil.cleanup_working_dir()
