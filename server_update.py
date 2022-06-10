from __future__ import annotations

import sys

# Before we do ANYTHING, we check to make sure python is the correct version!

if sys.version_info < (3,7,0):

    sys.stdout.write("\n--== [ Invalid python version! ] ==--\n")
    sys.stdout.write("Current version: {}\n".format(version_info))
    sys.stdout.write("Expected version: 3.7+\n")
    sys.stdout.write("\nPlease install the correct version of python before continuing!\n")

    sys.exit()

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
from typing import Any, Callable, List, Sequence, Tuple, Union
from json.decoder import JSONDecodeError
from math import ceil


"""
A Set of tools to automate the server update process.
"""

__version__ = '2.2.1'

# These variables contain links for the script updating process.

GITHUB = 'https://github.com/Owen-Cochell/PaperMC-Update'
GITHUB_RELEASE = 'https://api.github.com/repos/Owen-Cochell/PaperMC-Update/releases/latest'
GITHUB_RAW = 'https://raw.githubusercontent.com/Owen-Cochell/PaperMC-Update/master/server_update.py'


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


def upgrade_script(serv: ServerUpdater):
    """
    Upgrades this script.
    
    We do this by checking github for any new releases,
    comparing them to our version,
    and then updating if necessary.
    
    We use the ServerUpdater to do this operation for us,
    so you will need to provide it for this function
    to work correctly.

    :param serv: ServerUpdater to use
    :type serv: ServerUpdater
    """
    
    output("# Checking for update ...")
    
    # Creating request here:
    
    req = urllib.request.Request(GITHUB_RELEASE, headers={'Accept': 'application/vnd.github.v3+json'})

    # Getting data:
    
    data = json.loads(urllib.request.urlopen(req).read())

    # Checking if the version is new:

    if data['tag_name'] == __version__:

        # No update necessary, lets log and exit:

        output("# No update necessary!\n")

        return

    output("# New version available!")

    url = GITHUB_RAW
    path = os.path.realpath(__file__)

    # Determine if we are working in a frozen environment:
    
    if getattr(sys, 'frozen', False):
        
        print("# Can't upgrade frozen files!")

        return

    serv.fileutil.path = path

    # Getting data:

    data = urllib.request.urlopen(urllib.request.Request(url))

    # Write the data:
    
    serv.fileutil.create_temp_dir()

    temp_path = os.path.realpath(serv.fileutil.temp.name + '/temp')

    file = open(temp_path, mode='wb')

    file.write(data.read())

    # Install the new script:

    serv.fileutil.install(temp_path, path)

    # We are done!

    output("# Script update complete!\n")


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


        if hasattr(exc, 'url'):

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


def progress_bar(length: int, stepsize: int, total_steps: int, step: int, prefix: str="Downloading:", size: int=60, prog_char: str="#", empty_char: str="."):
    """
    Outputs a simple progress bar to stdout.

    We act as a generator, continuing to iterate and add to the bar progress
    as we download more information.

    :param legnth: Length of data to download
    :type length: int
    :param stepsize: Size of each step
    :type stepsize: int
    :param total_steps: Total number of steps
    :type total_steps: int
    :param step: Step number we are on
    :type step: int
    :param prefix: Prefix to use for the progress bar
    :type prefix: str
    :param size: Number of characters on the progress bar
    :type size: int
    :param prog_char: Character to use for progress
    :type prog_char: str
    :param empty_char: Character to use for empty progress
    :type empty_char: str
    """

    # Calculate number of '#' to render:

    x = int(size*(step+1)/total_steps)

    # Rendering progress bar:

    if not args.quiet:

        sys.stdout.write("{}[{}{}] {}/{}\r".format(prefix, prog_char*x, empty_char*(size-x),
                                                        (step*stepsize if step < total_steps - 1 else length), length))
        sys.stdout.flush()

    if not args.quiet and step >= total_steps - 1 :

        sys.stdout.write("\n")
        sys.stdout.flush()


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

    def _none_function(self, length, blocksize, total, step, *args, **kwargs):
        """
        Dummy function that does nothing.
        """

        pass

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

        temp: List[int] = []

        for item in ver.split('.'):

            # Convert and add the item:

            temp.append(int(item))

        return (temp[0], temp[1], temp[2])

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

    def download_file(self, path: str, version: str, build_num:int, check:bool=True, call: Callable=None, args: List=None, blocksize: int=4608) -> str:
        """
        Downloads the content to the given external file.
        We handle all file operations,
        and automatically work with the URLResponse objects
        to write the file contents to an external file.

        If a directory is provided, 
        then we will use the recommended name of the file,
        and save it to the directory provided.

        Users can also pass a function to be called upon each block of the download.
        This can be useful to visualize or track downloads.
        We will pass the total length, stepsize, total steps, and step number.
        The args provided in the args parameters will be passed to the function as well.

        :param path: Path to directory to write to
        :type path: str
        :param version: Version to download
        :type version: str
        :param build_num: Build to download
        :type build_num: int
        :param check: Boolean determining if we should check the integrity of the file
        :type check: bool
        :param call: Method to call upon each download iteration
        :type call: Callable
        :param args: Args to pass to the callable
        :type args: List
        :param blocksize: Number of bytes to read per copy operation
        :type blocksize: int
        :return: Path the file was saved to
        :raises: ValueError: If file integrity check fails
        """

        if args is None:

            args = []

        if call is None:

            call = self._none_function
            args = []

        # Get the data:

        data = self.download_response(version, build_num)

        # Get filename for download:

        if os.path.isdir(path):

            # Use the default name:

            path = os.path.join(path, data.getheader('content-disposition', default='').split("''")[1])

        # Get length of file:

        length = data.getheader('content-length')

        # Ensure result is not None:

        if length is None:

            # Raise an error:

            raise ValueError("Content length not present in HTTP headers!")

        # Otherwise, set the length:

        length = int(length)

        total = ceil(length/blocksize) + 1

        # Open the file:

        file = open(path, mode='ba')

        # Copy the downloaded data to the file:

        for i in range(total):

            # Call the method:

            call(length, blocksize, total, i, *args)

            # Get the data:

            file.write(data.read(blocksize))

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

        We utilize some basic caching to remember responses
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

    def __init__(self, path):

        self.path: str = os.path.abspath(path)  # Path to working directory
        self.temp: tempfile.TemporaryDirectory  # Tempdir instance
        self.config_default = 'version_history.json'  # Default name of paper versioning file
        self.target_path = ''  # Path the new file will be moved to

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

        if config is None:

            # Need to determine our config path:

            if os.path.isdir(self.path):

                config = os.path.join(self.path, self.config_default)

            else:

                config = os.path.join(os.path.dirname(self.path), self.config_default)

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

    def install(self, file_path: str, new_path: str, target_copy: str=None, backup=True, new=False):
        """
        "Installs" the contents of the temporary file into the target in the root server directory.

        The new file should exist in the temporary directory before this method is invoked!

        We backup the old jar file by default to the temporary directory,
        and we will attempt to recover the old jar file in the event of any failures.
        This feature can be disabled.

        :param file_path: The path to the new file to install
        :type new_file: str
        :param new_path: Path to install the file to
        :type new_path: str
        :param target_copy: Where to copy the old file to
        :type target_copy: str
        :param file_name: What to rename the new file to, None for no change
        :type file_name: str
        :param backup: Value determining if we should back up the old file
        :type backup: bool
        :param new: Determines if we are doing a new install, aka if we care about file operation errors
        :type new: bool
        """

        output("\n[ --== Installation: ==-- ]\n")

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

            self.target_path = new_path

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
            output("# ({} > {})".format(file_path, os.path.join(os.path.dirname(self.path), new_path)))

            # Copy to the new directory with the given name:

            shutil.copyfile(file_path, os.path.join(os.path.dirname(self.path), new_path))

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

        output("\n[ --== Installation complete! ==-- ]")

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

            os.remove(self.target_path)

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


class ServerUpdater:

    """
    Class that binds all server updater classes together
    """

    def __init__(self, path, config_file: str='', version='0', build=-1, config=True, prompt=True, integrity=True):

        self.version = version  # Version of minecraft server we are running
        self.buildnum = build  # Buildnum of the current server
        self.fileutil = FileUtil(path)  # Fileutility instance
        self.prompt = prompt  # Whether to prompt the user for version selection
        self.config_file = config_file  # Name of the config file we pull version info from
        self.integrity = integrity  # Boolean determining if we should run an integrity check
        self.version_install = None  # Version to install
        self.build_install = None  # Build to install
        self.config = config

        self.update = Update()  # Updater Instance

    def start(self):
        """
        Starts the object, loads configuration.
        """

        temp_version = '0'
        temp_build = 0

        if self.config:

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

    def view_data(self):
        """
        Displays data on the selected version and build.

        We display the version, build, time,
        commit changes, filename, and the sha256 hash.

        :param data: Dictionary to display
        :type data: dict
        """

        # Get the version we are working with:

        ver, build = self.version_select(args.version, args.build)

        # Check if install is aborted:
        
        if ver == '' or build == -1:

            # Error occurred, cancel stats operation

            return

        # Get the data:

        data = self.update.get(ver, build)

        output("\n+==================================================+")

        output("\n[ --== Paper Stats: ==-- ]\n")
        output("Version: {}".format(data['version']))
        output("Build Number: {}".format(data['build']))
        output("Creation Time: {}".format(data['time']))
        output("File name: {}".format(data['downloads']['application']['name']))
        output("SHA256 Hash: {}".format(data['downloads']['application']['sha256']))

        for num, change in enumerate(data['changes']):

            output("\nChange {}:\n".format(num))

            output("Commit ID: {}".format(change['commit']))
            output("Commit Summary: {}".format(change['summary']))
            output("Commit Message: {}".format(change['message']))

        output("\n[ --== End Paper Stats! ==-- ]\n")
        output("+==================================================+\n")

    def check(self, default_version: str, default_build: int):
        """
        Checks if a new version is available.

        :param default_version: Default version to install
        :type default_version: str
        :param default_build: Default build to install
        :type default_build: int
        :return: True is new version, False if not/error
        """

        output("[ --== Checking For New Version: ==-- ]\n")

        # Checking for new server version

        output("Loading version information ...")

        try:

            ver = self.update.get_versions()

        except URLError as e:

            self._url_report("API Fetch Operation")

            # Report the error

            error_report(e, net=True)

            return False

        except Exception as e:

            self._url_report("API Fetch Operation")

            # Report the error

            error_report(e)

            return False

        output("# Comparing local <> remote server versions ...")

        if self.version != self._select(default_version, ver, 'latest', 'version', print_output=False) and (self.version == '0' or ver[-1] != self.version):

            # New version available!

            output("# New Version available! - [Version: {}]".format(ver[-1]))
            output("\n[ --== Version check complete! ==-- ]")

            return True

        output("# No new version available.")

        # Checking builds

        output("# Loading build information ...")

        try:

            build = self.update.get_buildnums(self.version)

        except URLError as e:

            self._url_report("File Download")

            # Report the error

            error_report(e, net=True)

            return False

        except Exception as e:

            self._url_report("File Download")

            # Report the error

            error_report(e)

            return False

        output("# Comparing local <> remote builds ...")

        if self.buildnum != self._select(default_build, build, 'latest', 'buildnum', print_output=False) and (self.buildnum == 0 or build[-1] != self.buildnum):

            # New build available!

            output("# New build available! - [Build: {}]".format(build[-1]))
            output("\n[ --== Version check complete! ==-- ]")

            return True

        output("# No new builds found.")
        output("\n[ --== Version check complete! ==-- ]")

        return False

    def version_select(self, default_version: str='latest', default_build: int=-1) -> Tuple[str, int]:
        """
        Prompts the user to select a version to download,
        and checks input against values from Paper API.
        Default value is recommended option, usually 'latest'.

        :param default_version: Default version
        :type default_version: str
        :param default_build: Default build number
        :type default_build: int
        :return: (version, build)
        """

        if self.version_install is not None and self.build_install is not None:

            # Already have a version and build selected, return:

            return self.version_install, self.build_install

        output("\n[ --== Version Selection: ==-- ]\n")

        new_default = str(default_build)

        if new_default == '-1':

            # Convert into something more readable:

            new_default: str = 'latest'

        # Checking if we have version information:

        output("# Loading version information ...")

        try:

            versions = self.update.get_versions()

        except URLError as e:

            self._url_report("API Fetch Operation")

            # Report the error

            error_report(e, net=True)

            return '', -1

        except Exception as e:

            self._url_report("API Fetch Operation")

            # Report the error

            error_report(e)

            return '', -1

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

                ver = self._select(ver, versions, default_version, "version")

                if ver:

                    # User selected okay value

                    break

        else:

            # Just select default version

            ver = self._select('', versions, default_version, "version")

            if not ver:

                # Invalid version selected

                print("# Aborting installation!")

                return '', -1

        # Getting build info

        output("# Loading build information ...")

        try:

            nums = list(self.update.get_buildnums(ver))

        except URLError as e:

            self._url_report("API Fetch Operation")

            # Report the error

            error_report(e, net=True)

            return '', -1

        except Exception as e:

            self._url_report("API Fetch Operation")

            # Report the error

            error_report(e)

            return '', -1

        # Check if their are no builds:
        
        if len(nums) == 0:
            
            # No builds available, abort:

            print("# No builds available!")
            print("\nThe version you have selected has no builds available.")
            print("This could be because the version you are attempting to install is too new or old.")
            print("The best solution is to either wait for a build to be produced for your version,")
            print("Or select a different version instead.")

            print("\nTo see if a specific version has builds, you can issue the following command:\n")
            print("python server_update.py -nc --version [version]")
            print("\nSimply replace [version] with the version you wish to check.")
            print("This message will appear again if there are still no builds available.")
            print("The script will now exit.")

            return '', -1

        if self.prompt:

            print("\nPlease enter the build you would like to download:")
            print("Example: 205")
            print("(Tip: The value enclosed in brackets is the default option. Leave the prompt blank to accept it.)")
            print("(Tip: Enter 'latest' to select the latest build.)")

            print("\nAvailable Builds:")

            # Displaying available builds

            new = []

            for i in nums:

                print("  > Build Num: [{}]".format(i))
                new.append(str(i))

            while True:

                # Prompting user for build info

                build = input("\nEnter Build[{}]: ".format(new_default))

                print(new_default)

                build = self._select(build, new, new_default, "build")

                if build:

                    # User selected okay value
 
                    break

        else:

            # Select default build

            build = self._select('', nums, new_default, "build")

            if not build:

                # Invalid build selected!

                output("# Aborting installation!")

                return '', -1

        output("\nYou have selected:")
        output("   > Version: [{}]".format(ver))
        output("   > Build: [{}]".format(build))

        output("\n[ --== Version Selection Complete! ==-- ]")

        # Setting our values:

        self.version_install = str(ver)
        self.build_install = int(build)

        return self.version_install, self.build_install

    def get_new(self, default_version: str='latest', default_build: int=-1, backup: bool=True, new: bool=False, 
            target_copy: str=None, output_name: str=None):
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

        if ver == '' or build == -1:

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

        output("\n# Creating temporary directory...")

        self.fileutil.create_temp_dir()

        output("# Temporary directory created at: {}".format(self.fileutil.temp.name))

        # Starting download process:

        output("\n[ --== Starting Download: ==-- ]\n")

        try:

            path = self.update.download_file(self.fileutil.temp.name, ver, build_num=build, call=progress_bar, check=self.integrity)

        except URLError as e:

            self._url_report("File Download")

            # Report the error

            error_report(e, net=True)

            return False

        except ValueError as e:

            print("\n+==================================================+")
            print("> !ATTENTION! <")
            print("The file integrity check failed!")
            print("This means that the file downloaded is corrupted or damaged in some way.")
            print("Your current install (if one is targeted) has not been altered.")
            print("\nThere are many different causes for this error to occur.")
            print("It is likely that this is a one-off event.")
            print("Try again, and if this command continues to fail,")
            print("then your network or device might have a problem.")

            error_report(e)

            return False

        except Exception as e:

            self._url_report("File Download")

            # Report the error

            error_report(e)

            return False

        if self.integrity:

            output("# Integrity test passed!")

        output("# Saved file to: {}".format(path))

        output("\n[ --== Download Complete! ==-- ]")

        # Determining output name:

        target = self.fileutil.path

        # No output name defined via argument or path:

        if output_name is None and os.path.isdir(self.fileutil.path):

            # Keep original name:

            target = os.path.join(self.fileutil.path, os.path.split(path)[-1])

        # Output name specified via argument but not path:

        elif output_name is not None and os.path.isdir(self.fileutil.path):

            # Save file with custom name:

            target = os.path.join(self.fileutil.path, output_name)

        # Output name specified via argument and path:

        elif output_name is not None and os.path.isfile(self.fileutil.path):

            # Save file with custom name other than filename in path:

            target = os.path.join(os.path.dirname(self.fileutil.path), output_name)

        # Installing file:

        val = self.fileutil.install(path, target, backup=backup, new=new, target_copy=target_copy)

        if not val:

            # Install process failed

            return

        # Cleaning up temporary directory:

        output("\n# Cleaning up temporary directory...")

        self.fileutil.close_temp_dir()

        output("# Done cleaning temporary directory!")

        output("\nUpdate complete!")

        # Updating values

        self.version = ver
        self.buildnum = build

        return

    def _select(self, val: Any, choice: Sequence[Any], default: str, name: str, print_output: bool=True) -> Union[str, None]:
        """
        Selects a value from the choices.
        We support updater keywords,
        like 'latest', 'current' and ''.

        :param val: Value entered
        :type val: Any
        :param choice: Choices to choose from
        :type choice: Sequence[Any]
        :param default: Default value
        :type default: str
        :param name: Name of value we are choosing
        :type name: str
        :param print_output: Boolean determining if we output choices
        :type print_output: bool
        :return: Selected value, None if invalid
        :rtype: str, None
        """

        if val == '':

            # User wants default value:

            val = default

        if val == 'latest' or val == -1:

            # User wants latest

            if print_output:

                output("# Selecting latest {} - [{}] ...".format(name, choice[-1]))

            val = choice[-1]

            return val

        if val == 'current':
            
            if name == 'version':
            
                # User wants currently installed version:
                
                val = self.version
                
            elif name == 'build':
                
                val = self.buildnum

        if val not in choice:

            # User selected invalid option

            if print_output:

                output("\n# Error: Invalid {} selected!".format(name))

            return None

        # Option selected is valid. Continue

        if print_output:

            output("# Selecting {}: [{}] ...".format(name, val))

        return val

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


if __name__ == '__main__':

    # Ran as script

    parser = argparse.ArgumentParser(description='PaperMC Server Updater.',
                                     epilog="Please check the github page for more info: "
                                            "https://github.com/Owen-Cochell/PaperMC-Update.")

    parser.add_argument('path', help='Path to paper jar file', default=os.path.dirname(__file__) + '/', nargs='?')

    version = parser.add_argument_group('Version Options', 'Arguments for selecting and altering server version information')

    # +===========================================+
    # Server version arguments:

    version.add_argument('-v', '--version', help='Server version to install(Sets default value)', default='latest', type=str)
    version.add_argument('-b', '--build', help='Server build to install(Sets default value)', default=-1, type=str)
    version.add_argument('-iv', help='Sets the currently installed server version, ignores config', default='0', type=str)
    version.add_argument('-ib', help='Sets the currently installed server build, ignores config', default=0, type=int)
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
    file.add_argument('-co', '--copy-old', help='Copies the old file to a new location')
    file.add_argument('-ni', '--no-integrity', help='Skips the file integrity check', action='store_false')

    # +===========================================+
    # General command line arguments:

    parser.add_argument('-c', '--check-only', help='Checks for an update, does not install', action='store_true')
    parser.add_argument('-nc', '--no-check', help='Does not check for an update, skips to install', action='store_true')
    parser.add_argument('-i', '--interactive', help='Prompts the user for the version they would like to install',
                        action='store_true')
    parser.add_argument('-q', '--quiet', help="Will only output errors and interactive questions to the terminal",
                        action='store_true')
    parser.add_argument('-s', '--stats', help='Displays statistics on the selected version and build', action='store_true')
    parser.add_argument('-V', '--script-version', help='Displays script version', version=__version__, action='version')
    parser.add_argument('-u', '--upgrade', help='Upgrades this script to a new version if necessary, and exits', action='store_true')

    # Deprecated arguments - Included for compatibility, but do nothing

    parser.add_argument('-ndc', '--no-dump-config', help=argparse.SUPPRESS, action='store_false')
    parser.add_argument('--config', help=argparse.SUPPRESS, default='NONE')
    parser.add_argument('-C', '--cleanup', help=argparse.SUPPRESS, action='store_true')
    parser.add_argument('-nr', '--no-rename', help=argparse.SUPPRESS)

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
                         version=args.iv, build=args.ib, integrity=args.no_integrity)

    update_available = True

    # Determine if we should upgrade:

    if args.upgrade:
    
        output("Checking for script update ...")
    
        upgrade_script(serv)
        
        sys.exit()

    # Start the server updater

    serv.start()

    # Figure out the output name:

    name = None

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

    # Check for displaying stats:

    if args.stats:

        # Display stats to the terminal:

        serv.view_data()

    # Checking if we are skipping the update

    if not args.no_check and not args.new:

        # Allowed to check for update:

        update_available = serv.check(args.version, args.build)

    # Checking if we can install:

    if not args.check_only and update_available:

        # Allowed to install/Can install

        serv.get_new(default_version=args.version, default_build=args.build, backup=not (args.no_backup or args.new),
                    new=args.new, output_name=name, target_copy=args.copy_old)
