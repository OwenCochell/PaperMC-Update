from sys import version_info, stdout

# Before we do ANYTHING, we check to make sure python is the correct version!

if version_info < (3,6,0):

    stdout.write("\n--== [ Invalid python version! ] ==--\n")
    stdout.write("Current version: {}\n".format(version_info))
    stdout.write("Expected version: 3.6+\n")
    stdout.write("\nPlease install the correct version of python before continuing!\n")

    exit()

import tempfile
import urllib.request
import os
import shutil
import json
import traceback
import argparse

from urllib.error import URLError
from http.client import HTTPResponse
from hashlib import sha256
from typing import Tuple
from json.decoder import JSONDecodeError


"""
A Set of tools to automate the server update process.
"""

__version__ = '1.4.0'


def load_config(config: str) -> Tuple[str, int]:
    """
    Loads configuration data from the given file.

    We only load version info if it's in the official format!
    We return the version and build number found in the configuration file.

    :param config: Path to config file
    :type config: str
    :return: Tuple contaning version and build data respectively
    :rtype: Tuple[str, int]
    """

    # Exists and is file, read it

    file = open(config, 'r')

    data = json.load(file)

    # Read the data, and attempt to pull some info out of it

    current = data['currentVersion']

    # Splitting the data in two so we can pull some content out:

    build, version = current.split(" ", 1)

    # Getting build information:

    build = int(build.split("-")[-1])

    # Getting version information:

    version = version[5:-1]

    # Returning version information:

    return version, build


def output(text: str):

    """
    Outputs text to the terminal via print,
    will not print content if we are in quiet mode.
    """

    if not args.quiet:

        # We are not quieted, print the content

        print(text)


def error_report(exc, net: bool=False):
    """
    Function for displaying error information to the terminal.

    :param exc: Exception object
    :param net: Whether to include network information
    :type net: bool
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

    if net:

        # Include extra network information

        print("+==================================================+")
        print("Extra Network Information:")

        print("Attempted URL: {}".format(exc.url))

        if hasattr(exc, 'reason'):

            print("We failed to reach the server.")
            print("Reason: {}".format(exc.reason))

        if hasattr(exc, 'code'):

            print("The server could not fulfill the request.")
            print("Error code: {}".format(exc.code))

    print("+==================================================+")
    print("(Can you make anything of this?)")
    print("Please check the github page for more info: https://github.com/Owen-Cochell/PaperMC-Update.")

    return


class Update:
    """
    Server updater, handles checking, downloading, and installing.

    This class facilitates communication between this script and the Paper v2 API.
    We offer methods to retrieve available versions, builds, 
    and other information about downloads.
    Users can download the final jar file using this class as well.
    We also offer the ability to generate download URLs,
    so the user can download the files in any way they see fit. 
    """

    def __init__(self):

        self._base = 'https://papermc.io/api/v2/projects/paper'  # Base URL to build of off
        self._headers = {
             'Content-Type': 'application/json;charset=UTF-8',
             'Accept': 'application/json, text/plain, */*',
             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:43.0) Gecko/20100101 Firefox/43.0',
             'Accept-Language': 'en-US,en;q=0.5',
             'DNT': '1',
         }  # Request headers for contacting Paper Download API, emulating a Firefox client

        self.download_path = ''  # Path the file was downloaded to

        self.cache = {}  # A basic cache for saving responses

    def _progress_bar(self, total, step, end , prefix="", size=60, prog_char="#", empty_char="."):
        """
        Outputs a simple progress bar to stdout.

        We act as a generator, continuing to iterate and add to the bar progress
        as we download more information.

        :param total: Total amount of computations
        :param step: Amount to increase the counter by
        :param end:  Number to end on
        :param prefix: What to show before the progress bar
        :param size: Size of the progress bar
        """

        # Iterating over the total number of iterations:

        for i in range(total):

            # Yield i

            yield i

            # Calculate number of '#' to render:

            x = int(size*(i+1)/total)

            # Rendering progress bar:

            if not args.quiet:

                stdout.write("{}[{}{}] {}/{}\r".format(prefix, prog_char*x, empty_char*(size-x),
                                                           (i*step if i < total - 1 else end), end))
                stdout.flush()

        # Writing newline, to continue execution

        if not args.quiet:

            stdout.write("\n")
            stdout.flush()

    def _url_report(self, point: str):
        """
        Reports an error during a request operation.

        :param point: Point of failure
        :type point: str
        """

        print("\n+==================================================+")
        print("> !ATTENTION! >")
        print("An error occurred during a request operation.")
        print("Fail Point: {}".format(point))
        print("Your check/update operation will be canceled.")
        print("Detailed error info below:")

    def version_convert(self, ver: str) -> Tuple[int,int,int]:
        """
        Converts the version string into a tuple that can be used for comparison.

        This tuple contains three numbers, each of which can be used
        in equality operations.
        This can be used to determine if a given version is greater or lessor than another.

        :param ver: Version string to convert
        :type ver: str
        :return: Tuple contaning version information
        :rtype: Tuple[int,int,int]
        """

        # Convert and return the tuple:

        final = []

        for item in ver.split('.'):

            # Convert and add the item:

            final.append(int(item))

        # Return the final tuple:

        return tuple(final)

    def build_data_url(self, version: str=None, build_num: int=None) -> str:
        """
        Builds a valid URL for retrieving version data.

        The user can use this URL to retrieve various versioning data.

        If version and build_num are not specified,
        then general paper info is returned:

        https://papermc.io/api/v2/projects/paper

        If build_num is not specified, 
        then general data about the specified data is returned:

        https://papermc.io/api/v2/projects/paper/versions/[version]

        If both arguments are provided,
        then data about the specific version and build is returned:

        https://papermc.io/api/v2/projects/paper/versions/[version]/builds/[build_num]

        :param version: Version to fetch info for, defaults to None
        :type version: str, optional
        :param build_num: Build number to get info for, defaults to None
        :type build_num: int, optional
        :return: URL of the data
        :rtype: str
        """

        # Building url:

        final = self._base

        if version is not None:

            # Specific version requested:

            final = final + '/versions/' + str(version)

            if build_num is not None:

                # Specific build num requested:

                final = final + '/builds/' + str(build_num)

        # Return the URL:

        return final

    def build_download_url(self, version: str, build_num:int):
        """
        Builds a valid download URL that can be used to download a file.
        We use the version and build number to generate this URL.

        The user can use this URL to download the file
        using any method of their choice.

        :param version: Version to download
        :type version: str
        :param build_num: Build number to download, defaults to 'latest'
        :type build_num: str, optional
        """

        # Get download name

        download_name = self.get(version, build_num)['downloads']['application']['name']

        # Build and return the URL:

        return self._base + '/versions/' + str(version) + '/builds/' + str(build_num) + '/downloads/' + str(download_name)

    def download_response(self, version: str, build_num:int) -> HTTPResponse:
        """
        Calls the underlying urllib library and return the object generated.

        This object is usually a HTTPResponse object.
        The user can use this object in any way they see fit.
        We automatically generate the URL using the version and build_num given.

        :param url: URL of file to download
        :type url: str
        :return: Object returned by urllib
        :rtype: HTTPResponse
        """

        # Build the URL

        url = self.build_download_url(version, build_num)

        # Creating request here:

        req = urllib.request.Request(url, headers=self._headers)

        # Sending request to Paper API

        return urllib.request.urlopen(req)

    def download_file(self, path: str, version: str, build_num:int, check:bool=True):
        """
        Donloads the content to the given external file.
        We handle all file operations,
        and automatically work with the URLResponse objects
        to write the file contents to an external file.

        If a directory is provided, 
        then we will use the recommended name of the file,
        and save it to the directory provided.

        :param path: Path to directory to write to
        :type path: str
        :param version: Version to download
        :type version: str
        :param build_num: Build to download
        :type build_num: int
        :param check: Boolean determining if we should check the integrity of the file
        :type check: bool
        :return: Path the file was saved to
        :raises: ValueError: If file integrity check fails
        """

        # Get the data:

        data = self.download_response(version, build_num)

        # Getting content length of download:

        blocksize = 4608

        # Get filename for download:

        if os.path.isdir(path):

            # Use the default name:

            path = os.path.join(path, data.getheader('content-disposition', default='').split("''")[1])
        
        # Open the file:

        file = open(path, mode='ba')

        # Copy the downloaded data to the file:

        shutil.copyfileobj(data, file, blocksize)

        # Close the file:

        file.close()

        # Re-open the file for reading:

        file = open(path, mode='rb')

        if check:

            # Get the ideal SHA256 hash for the file:

            hash = self.get(version, build_num)['downloads']['application']['sha256']

            # Checking integrity:

            if not sha256(file.read()).hexdigest() == hash:

                # File integrity failed! Do something...

                raise ValueError("File integrity check failed!")

        # Closing file:

        file.close()

        return path

    def get_versions(self) -> Tuple[str,...]:
        """
        Gets available versions of the server.

        The list of versions is a tuple of strings.
        Each version follows the Minecraft game version conventions.

        :return: List of available versions
        """

        # Returning version info

        return self.get()['versions']

    def get_buildnums(self, version: str) -> Tuple[int,...]:
        """
        Gets available build for a particular version.

        The builds are a tuple of ints,
        which follow PaperMC build number conventions.

        :param version: Version to get builds for
        :type version: str
        :return: List of builds
        :rtype: Tuple[int,...]
        """

        # Returning build info:

        return self.get(version)['builds']

    def get(self, version: str=None, build_num: int=None) -> dict:
        """
        Gets RAW data from the Paper API, version info only.

        We utilise some basic caching to remember responses
        instead of calling the PaperMC API multiple times. 

        You can use this to get a list of valid versions,
        list of valid builds per version,
        as well as general data related to the selected version.

        You should check out:

        https://paper.readthedocs.io/en/latest/site/api.html
        https://papermc.io/api/docs/swagger-ui/index.html?configUrl=/api/openapi/swagger-config#/

        For more information on PaperMC API formatting.

        We return the data in a dictionary format.

        :param version: Version to include in the URL
        :type version: str
        :param build_num: Build number to include in the URL
        :type build_num: int
        :return: Dictionary of request data
        :rtype: dict
        """

        # Generate URL:

        url = self.build_data_url(version, build_num)

        # Check if we have saved content:

        if url in self.cache.keys():

            # We have cached content:

            return self.cache[url]

        # Get the data and return:

        data = json.loads(self._get(version, build_num).read())

        # Cache it:

        self.cache[url] = data

        # Return the final data:

        return data

    def _get(self, version: str=None, build_num: int=None) -> HTTPResponse:
        """
        Gets raw data from the PaperMC download API.

        This method generates the relevant URLs and returns
        the HTTPResponse object representing the request.

        :param version: Version to get info for, defaults to None
        :type version: str, optional
        :param build_num: Build to get info for, defaults to None
        :type build_num: int, optional
        :return: HTTPResponse representing the request
        :rtype: HTTPResponse
        """

        final = self.build_data_url(version, build_num)

        print(final)

        # Check if the URL is present in the cache:

        if final in self.cache.keys():

            # Cached content is found, return THAT:

            return self.cache[final]

        # Creating request here:

        req = urllib.request.Request(final, headers=self._headers)

        # Getting data:

        data = urllib.request.urlopen(req)

        # Saving data:

        self.cache[final] = data

        return data


class FileUtil:
    """
    Class for managing the creating/deleting/moving of server files.
    """

    def __init__(self, path, config=None):

        self.path: str = os.path.abspath(path)  # Path to working directory
        self.temp: tempfile.TemporaryDirectory  # Tempdir instance
        self.config_default = 'version_history.json'  # Default name of paper versioning file

    def create_temp_dir(self):
        """
        Creates a temporary directory.

        :return: Temp file instance
        """

        self.temp = tempfile.TemporaryDirectory()

        return self.temp

    def close_temp_dir(self):
        """
        Closes created temporary directory.
        """

        self.temp.cleanup()

    def load_config(self, config: str) -> Tuple[str, int]:
        """
        Loads configuration info from 'version.json' in the server directory
        We only load version info if it's in the official format!

        :param config: Path to config file
        :type config: str
        :return: Configuration info from file
        :rtype: Tuple[str, int]
        """

        config = (config if config is not None else os.path.join(os.path.dirname(self.path), self.config_default))

        output("# Loading configuration data from file [{}] ...".format(config))

        if os.path.isfile(config):

            try:

                return load_config(config)

            except JSONDecodeError:

                # Data not in valid JSON format.

                output("# Failed to load config data - Not in JSON format!")

                return '0', 0

            except Exception:

                # Extra weird errors due to formatting issues:

                output("# Failed to load config data - Strange format, we support official builds only!")

                return '0', 0

        else:

            print("# Unable to load config data from file at [{}] - Not found/Not a file!".format(config))

            return '0', 0

    def _fail_install(self, point):

        """
        Shows where the error occurred during the installation.

        :param point: Point of failure
        """

        print("\n+==================================================+")
        print("> !ATTENTION! <")
        print("An error occurred during the installation, and we can not continue.")
        print("We will attempt to recover your previous installation(If applicable)")
        print("Fail point: {}".format(point))
        print("Detailed error info below:")

        return

    def install(self, file_path: str, target_copy: str=None, file_name: str=None, backup=True, new=False):
        """
        "Installs" the contents of the temporary file into the target in the root server directory.

        The new file should exist in the temporary directory before this method is invoked!

        We backup the old jar file by default to the temporary directory,
        and we will attempt to recover the old jar file in the event of any failures.
        This feature can be disabled.

        :param file_path: The path to the new file to install
        :type new_file: str
        :param target_copy: Where to copy the old file to
        :type target_copy: str
        :param file_name: What to rename the new file to, None for no change
        :type file_name: str
        :param backup: Value determining if we should back up the old file
        :type backup: bool
        :param new: Determines if we are doing a new install, aka if we care about file operation errors
        :type new: bool
        """

        # Resolve output filename:

        if file_name is None:

            file_name = os.path.basename(file_path)

        output("\n[ --== Installation: ==-- ]")

        # Checking if we should copy the old file:

        if target_copy is not None and os.path.isfile(self.path):

            # Copy the old file:

            output("# Copying old file ...")
            output("# ({} > {})".format(self.path, target_copy))

            try:

                shutil.copy(self.path, target_copy)

            except Exception as e:

                # Copy error:

                self._fail_install("Old File Copy")

                # Report the error:

                error_report(e)

                # Exit, install failed!

                return False

        # Creating backup of old file:

        if backup and os.path.isfile(self.path) and not new:

            output("# Creating backup of previous installation ...")

            try:

                shutil.copyfile(self.path, os.path.join(self.temp.name, 'backup'))

            except Exception as e:

                # Show install error

                self._fail_install("File Backup")

                # Show error info

                error_report(e)

                return False

            output("# Backup created at: {}".format(os.path.join(self.temp.name, 'backup')))

        # Determine if we should delete the original file:

        if os.path.isfile(self.path) and not new:

            # Removing current file:

            output("# Deleting current file at {} ...".format(self.path))

            try:

                os.remove(self.path)

            except Exception as e:

                if not new:

                    self._fail_install("Old File Deletion")

                    # Showing error

                    error_report(e)

                    # Recovering backup

                    if backup:

                        self._recover_backup()

                    return False

            output("# Removed original file!")

        # Copying downloaded file to root:

        try:

            output("# Copying download data to root directory ...")
            output("# ({} > {})".format(file_path, os.path.join(os.path.dirname(self.path), file_name)))

            if file_name is None:

                # Do not rename the downloaded file!

                shutil.copy(file_path, os.path.dirname(self.path))

            else:

                # Copy to the new directory with the given name:

                shutil.copyfile(file_path, os.path.join(os.path.dirname(self.path), file_name))

        except Exception as e:

            # Install error

            self._fail_install("File Copy")

            # Show error

            error_report(e)

            # Recover backup

            if backup and os.path.isfile(self.path) and not new:

                self._recover_backup()

                return False

            return False

        output("# Done copying download data to root directory!")

        output("[ --== Installation complete! ==-- ]")

        return True

    def _recover_backup(self):
        """
        Attempts to recover the backup of the old server jar file.
        """

        print("+==================================================+")
        print("\n> !ATTENTION! <")
        print("A failure has occurred during the installation process.")
        print("I'm sure you can see the error information above.")
        print("This script will attempt to recover your old installation.")
        print("If this operation fails, check the github page for more info: "
              "https://github.com/Owen-Cochell/PaperMC-Update")

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

            print("Your previous installation could not be recovered.")

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

            print("Your previous installation could not be recovered.")

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

    def __init__(self, path, config_file: str='', version='0', build=0, config=True, prompt=True):

        self.version = version  # Version of minecraft server we are running
        self.fileutil = FileUtil(path)  # Fileutility instance
        self.buildnum = build  # Buildnum of the current server
        self._available_versions = []  # List of available versions
        self.prompt = prompt  # Whether to prompt the user for version selection
        self.config_file = config_file  # Name of the config file we pull version info from

        # Starting object

        self._start(config)

        self.update = Update()  # Updater Instance

    def _start(self, config):
        """
        Starts the object, loads configuration.
        """

        temp_version = '0'
        temp_build = 0

        if config:

            # Allowed to use configuration file

            temp_version, temp_build = self.fileutil.load_config(self.config_file)

        else:

            # Skipping config file

            output("# Skipping configuration file!")

        self.version = (self.version if self.version != '0' else temp_version)
        self.buildnum = (self.buildnum if self.buildnum != 0 else temp_build)

        self.report_version()

        return

    def report_version(self):
        """
        Outputs the current server version and build to the terminal.
        """

        output("\nServer Version Information:")
        output("  > Version: [{}]".format(self.version))
        output("  > Build: [{}]".format(self.buildnum))

    def check(self):
        """
        Checks if a new version is available.

        :return: True is new version, False if not/error
        """

        output("\n[ --== Checking For New Version: ==-- ]")

        # Checking for new server version

        output("# Comparing local <> remote server versions...")

        ver = self.update.get_versions()

        if self.version == '0' or ver[-1] != self.version:

            # New version available!

            output("# New Version available! - [Version: {}]".format(ver[-1]))
            output("[ --== Version check complete! ==-- ]\n")

            return True

        output("# No new version available.")

        # Checking builds

        output("# Comparing local <> remote builds...")

        build = self.update.get_buildnums(self.version)

        if self.buildnum == 0 or build[-1] != self.buildnum:

            # New build available!

            output("# New build available! - [Build: {}]".format(build[-1]))
            output("[ --== Version check complete! ==-- ]\n")

            return True

        output("# No new builds found.")
        output("[ --== Version check complete! ==-- ]\n")

        return False

    def version_select(self, default_version='latest', default_build='latest'):
        """
        Prompts the user to select a version to download,
        and checks input against values from Paper API.
        Default value is recommended option, usually 'latest'.

        :param default_build: Default build number
        :param default_version: Default version
        :return: (version, build)
        """

        # Checking if we have version information:

        output("# Checking version information ...")

        versions = self.update.get_versions()

        if self.prompt:

            print("\n[ --== Version Select: ==-- ] ")

            print("\nPlease enter the version you would like to download:")
            print("Example: 14.4.4")
            print("(Tip: The value enclosed in brackets is the default option. Leave the prompt blank to accept it.)")
            print("(Tip: Enter 'latest' to select the latest version.)")

            print("\nAvailable versions:")

            # Displaying available versions

            for i in versions:

                print("  Version: [{}]".format(i))

            while True:

                ver = input("\nEnter Version[{}]: ".format(default_version))

                stat, ver = self._select(ver, versions, default_version, "version")

                if stat:

                    # User selected okay value

                    break

        else:

            # Just select default version

            stat, ver = self._select('', versions, default_version, "version")

            if not stat:

                # Invalid version selected

                print("# Aborting installation!")

                return None, None

        # Getting build info

        output("# Loading build information ...")

        nums = self.update.get_buildnums(ver)

        if self.prompt:

            print("\nPlease enter the build you would like to download:")
            print("Example: 205")
            print("(Tip: The value enclosed in brackets is the default option. Leave the prompt blank to accept it.)")
            print("(Tip: Enter 'latest' to select the latest build.)")

            print("\nAvailable Builds:")

            # Displaying available builds

            for num, i in enumerate(nums):

                print("  > Build Num: [{}]".format(i))

                nums[num] = str(i)

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

                output("# Aborting installation!")

                return None, None

        output("\nYou have selected:")
        output("   > Version: [{}]".format(ver))
        output("   > Build: [{}]".format(build))

        output("\n[ --== Version Selection Complete! ==-- ]")

        return ver, build

    def get_new(self, default_version='latest', default_build='latest', backup=True, new=False, target_copy=None, output_name=None):
        """
        Downloads and installs the new version,
        Prompts the user to select a specific version.

        After the version is selected,
        then we invoke the process of downloading the the file,
        and installing it to the current location.

        :param default_version: Default version to select if none is specified
        :type default_version: str
        :param default_build: Default build to select if none is specified
        :type default_build: str
        :param backup: Value determining if we should back up the old jar file
        :type backup: bool
        :param new: Value determining if we are doing a new install
        :type new: bool
        :param target_copy: Path we should copy the old file to
        :type no_delete: str
        :param output_name: Name of the new file. None to keep original name
        :type output_name: str
        """

        # Prompting user for version info:

        ver, build = self.version_select(default_version=default_version, default_build=default_build)

        if ver is None or build is None:

            # Error occurred, cancel installation

            return

        # Checking if user wants to continue with installation

        if self.prompt:

            print("\nDo you want to continue with the installation?")

            inp = input("(Y/N):").lower()

            if inp in ['n', 'no']:
                # User does not want to continue, exit

                output("Canceling installation...")

                return

        # Creating temporary directory to store assets:

        output("# Creating temporary directory...")

        self.fileutil.create_temp_dir()

        output("# Temporary directory created at: {}".format(self.fileutil.temp.name))

        # Starting download process:

        path = self.update.download_file(self.fileutil.temp.name, ver, build_num=build)

        # Installing downloaded data:

        val = self.fileutil.install(path, file_name=output_name, backup=backup, new=new, target_copy=target_copy)

        if not val:

            # Install process failed

            return

        # Cleaning up temporary directory:

        output("# Cleaning up temporary directory...")

        self.fileutil.close_temp_dir()

        output("# Done cleaning temporary directory!")

        output("\nUpdate complete!")

        # Updating values

        self.version = ver
        self.buildnum = build

        return

    def _select(self, val, choice, default, name):
        """
        Selects a value from the choices.
        We support updater keywords,
        like 'latest' and ''.

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

            output("# Selecting latest {} - [{}] ...".format(name, choice[-1]))

            val = choice[-1]

            return True, val

        if val not in choice:

            # User selected invalid option

            output("\n# Error: Invalid {} selected!".format(name))

            return False, ''

        # Option selected is valid. Continue

        output("# Selecting {}: [{}] ...".format(name, val))

        return True, val


if __name__ == '__main__':

    # Ran as script

    parser = argparse.ArgumentParser(description='PaperMC Server Updater.',
                                     epilog="Please check the github page for more info: "
                                            "https://github.com/Owen-Cochell/PaperMC-Update.")

    parser.add_argument('path', help='Path to paper jar file')

    version = parser.add_argument_group('Version Options', 'Arguments for selecting and altering server version information')

    # +===========================================+
    # Server version arguments:

    version.add_argument('-v', '--version', help='Server version to install(Sets default value)', default='latest')
    version.add_argument('-b', '--build', help='Server build to install(Sets default value)', default='latest')
    version.add_argument('-iv', help='Sets the currently installed server version, ignores config', default='0')
    version.add_argument('-ib', help='Sets the currently installed server build, ignores config', default=0)
    version.add_argument('-sv', '--server-version', help="Displays server version from configuration file and exits", action='store_true')

    # +===========================================+
    # File command line arguments:

    file = parser.add_argument_group("File Options", "Arguments for altering how we work with files")

    file.add_argument('-nlc', '--no-load-config', help='Will not load Paper version config', action='store_false')
    file.add_argument('-cf', '--config-file', help='Path to Paper configuration file to read from'
                                                     '(Defaults to [SERVER_JAR_DIR]/version_history.json)')
    file.add_argument('-nb', '--no-backup', help='Disables backup of the old server jar', action='store_true')
    file.add_argument('-n', '--new', help='Installs a new paper jar instead of updating. Great for configuring a new server install',
                        action='store_true')
    file.add_argument('-o', '--output', help='Name of the new file')
    file.add_argument('-nr', '--no-rename', help='Does not rename the new file, uses default jar name', action='store_true')
    file.add_argument('-co', '--copy-old', help='Copies the old file to a new location')
    
    # +===========================================+
    # General command line arguments:

    parser.add_argument('-c', '--check-only', help='Checks for an update, does not install', action='store_true')
    parser.add_argument('-nc', '--no-check', help='Does not check for an update, skips to install', action='store_true')
    parser.add_argument('-i', '--interactive', help='Prompts the user for the version they would like to install',
                        action='store_true')
    parser.add_argument('-q', '--quiet', help="Will only output errors and interactive questions to the terminal",
                        action='store_true')
    parser.add_argument('-V', '--script-version', help='Displays script version', version=__version__, action='version')


    # Deprecated arguments - Included for compatibility, but do nothing

    parser.add_argument('-ndc', '--no-dump-config', help=argparse.SUPPRESS, action='store_false')
    parser.add_argument('--config', help=argparse.SUPPRESS, default='NONE')
    parser.add_argument('-C', '--cleanup', help=argparse.SUPPRESS, action='store_true')

    args = parser.parse_args()

    output("+==========================================================================+")
    output(r'''|     _____                              __  __          __      __        |
|    / ___/___  ______   _____  _____   / / / /___  ____/ /___ _/ /____    |
|    \__ \/ _ \/ ___/ | / / _ \/ ___/  / / / / __ \/ __  / __ `/ __/ _ \   |
|   ___/ /  __/ /   | |/ /  __/ /     / /_/ / /_/ / /_/ / /_/ / /_/  __/   |
|  /____/\___/_/    |___/\___/_/      \____/ .___/\__,_/\__,_/\__/\___/    |
|                                         /_/                              |''')
    output("+==========================================================================+")
    output("\n[PaperMC Server Updater]")
    output("[Handles the checking, downloading, and installation of server versions]")
    output("[Written by: Owen Cochell]\n")

    serv = ServerUpdater(args.path, config_file=args.config_file, config=args.no_load_config or args.server_version, prompt=args.interactive,
                         version=args.iv, build=args.ib)

    update_available = True

    # Figure out the output name:

    name = None

    if not args.no_rename:

        if args.output:

            # Name was explicitly given to us:

            name = args.output

        elif os.path.basename(args.path) != '':

            # Get filename from the given path:

            name = os.path.basename(args.path)

    # Check if we are just looking for server info:

    if args.server_version:

        # Already printed it, lets exit

        exit()

    # Checking if we are skipping the update

    if not args.no_check and not args.new:

        # Allowed to check for update:

        update_available = serv.check()

    # Checking if we can install:

    if not args.check_only and update_available:

        # Allowed to install/Can install

        serv.get_new(default_version=args.version, default_build=args.build, backup=args.no_backup or args.new,
                    new=args.new, output_name=name, target_copy=args.copy_old)

