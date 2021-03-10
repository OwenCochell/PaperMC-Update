# PaperMC-Update
A simple CLI script for automating the checking, downloading, and installing of PaperMC server updates.

NOTE: This script can only be used for updating a [PaperMC Minecraft Server](https://papermc.io/). I highly recommend 
there implementation, as it is incredibly fast, supports multiple plugin formats, and is highly customizable. 
Consider changing if any of that sounds good to you. You can find the PaperMC documentation 
[Here](https://paper.readthedocs.io/en/latest/), and you can find their github page [Here](https://github.com/PaperMC).

# Prerequisites
You must have Python 3+ installed. It should come pre-installed on most linux systems. 
This script has no other dependencies, so all you need is python! Instructions for installation are below:

## Linux:

RPM:
>yum install python3.9

Debian:
>apt install python3.9

Or use whatever packet manager is installed on your system.
The only important part is specifying python3.9!

## Windows:

Windows users can download python [Here](https://www.python.org/downloads/windows/). The installation is very straightforward, 
although we recommend you add python to your PATH environment variable, as this makes using python much easier.

More information on installing/configuring python can be found [Here](https://www.python.org/downloads/).
(Any python 3 version works, although I recommend python 3.9)

We also supply windows binaries that can be ran directly on windows systems without python!
We use [PyInstaller](https://www.pyinstaller.org/) to build these binaries, and they are built using the one file option, or '-F'.

These binaries are much slower than running via python, and there might be some weird bugs or quirks.
They are built for windows only. We provide one with each version change.
Find them [here](https://github.com/Owen-Cochell/PaperMC-Update/releases) in the releases!

## MacOS:

MacOS users can download python [Here](https://www.python.org/downloads/mac-osx/).

Again, the installation is very straightforward, but more information can be found [Here](https://docs.python.org/3/using/mac.html).


# Usage

You may run the command like so:

> python server_update.py [PATH]

Where [PATH] is the path to your paperclip.jar file. More info on the paperclip.jar format can be found 
[Here](https://paper.readthedocs.io/en/latest/about/structure.html#id2). If a new file is downloaded, 
it will be installed to this path under the same name.

This command will do the following:

1. Attempt to load current paper version/build(`/PATH_TO_SERVER_JAR/version_history.json`, or elsewhere if specified. 
This script only supports official builds of the paper server, meaning that we may fail to read config 
information for un-official builds). If no configuration data is found, and version info is not supplied via the 
command line, then the version and build for the currently installed server will default to 0.
2. Check for a new version/build using the 
[PaperMC download API](https://paper.readthedocs.io/en/latest/site/api.html#downloads-api).
3. If a new version/build is available, the default version and build(usually the latest) will be installed.
If you wish to select a version/build to install, then you can use '--version' and '--build' arguments to specify this. 
Alternatively, the user can be prompted to manually select which version/build they want to be installed. You can use 
the `--interactive` flag for this.
4. The selected version is downloaded to a temporary directory located somewhere on your computer
(This directory is generated using the python tempfile module, meaning that it will be generated in a safe, 
unobtrusive manner, and will be automatically removed at termination of the script).
5. The currently installed version of the server is backed up to the temporary directory, and deleted.
This option can be disabled if you so choose.
6. The newly downloaded server jar is moved from the temporary directory to the path of the old server, 
and will retain the name of the old server(If an error occurs for any reason during the instillation procedure, 
then the script will attempt to recover your backed up version of the old server from the temporary directory).

This is the default operation of this script. However, you can fine tune the update process using the command line options
listed below.
# Command Line Options:

The following command line options are available:

Sets the default value for the version to install, defaults to latest:
>-v [VERSION], --version [VERSION]

Sets the default value for the build to install, defaults to latest:
>-b [BUILD], --build [BUILD]

Sets the currently installed server version, ignores config data:
>-iv [VERSION]

Sets the currently installed server build, ignores config data:
>-ib [BUILD]

Checks for an update, does not install:
>-c, --check-only

Does not check for an update, skips to install:
>-nc, --no-check

Prompts the user for the version they would like to install:
>-i, --interactive

Will not load configuration data:
>-nlc, --no-load-config

Sets config file path(`/PATH_TO_SERVER_JAR/version_history.json` by default):
>-cf, --config-file [PATH TO CONFIG FILE]

Disables the backup feature:
>-nb, --no-backup

Displays script version information:
>-V, --script-version

Displays server version, extracted from configuration file:
>-sv, --server-version

Will only output errors and interactive questions to the terminal:
>-q, --quiet

## Deprecated Command Line Options

The following command line options are deprecated. They are still included for backwards compatibility,
but they do nothing and should not be used.

Delete the config directory and all data within:
>-C, --cleanup

Will not dump configuration data:
>-ndc, --no-dump-config

Specify which config directory should be used, defaults to `/DIR_OF_YOUR_SERVER_JAR_FILE/server_update`:
>--config [PATH]

# Examples:

Automatically check and download the latest version of the server:
>python server_update.py [PATH]

Download and install the latest build of version 1.13.2, without checking:
>python server_update.py --no-check --version 1.13.2 [PATH]

Install latest version, regardless of server version:
>python server_update.py --no-check [PATH]

Install specific version, regardless of installed version:
>python server_update.py --no-check --version [VERSION TO INSTALL] --build [BUILD TO INSTALL] [PATH]

Interactively select a version you want to install, regardless of server version:
>python server_update.py --no-check --no-load --interactive [PATH]

Check to see if a newer version is available, does not install:
>python server_update.py --check-only [PATH]

Display currently installed server version:
>python server_update.py --server-version [PATH]

Install a paper jar at the given location, without going through the update process.
Great if you want to set up a new server install.
>python server_update.py --new [PATH]

# Notes on Deprecated Features

In earlier versions of PaperMC-Update, the script would keep a config file in the users home directory
(Or elsewhere if specified) containing version information on the server so it can be persistent across runs. 

There were many problems with this: it created unnecessary files, it was inaccurate, 
and it made using PaperMC-Update a lot more complicated. Now, we read version info from a file named 
'version_history.json', which is kept in the root directory of the server, and is managed by the server itself. This 
eliminates the need for 'script-generated configuration files', 
and makes PaperMC-Update easier to use and more accurate.

However, their are some things to keep in mind:

## Official Builds

As of now, PaperMC-Update only supports official builds of the server. As such, builds built locally or 
builds downloaded from unofficial sources may not be supported, 
due to the fact that the config file format might be different, meaning that we can't pull version information from it.

This is something I would like to change at a later date if possible. If you have some insight into the format of 
the config file across different builds, and have a way to identify and pull information from said file,
the please open a pull request. I would be happy to look it over! Be sure to include an example copy of the config 
file.

If you are using this script and see any of the following messages:

>Failed to load config data - Not in JSON format!

>Failed to load config data - We want strings, not [DATATYPE_HERE]!

>Unable to load config data - Invalid Format, we support official builds only!

Then please open an issue with the following information:

1. Description of what you were trying to do
2. All command arguments used
3. Version/build you were trying to install
4. Version/build of the currently installed server(If you know it)
5. A copy of your 'version_history.json'

I can use this information to not only fix the problems you are facing, but implement support 
for your build. 

## Command Line Options

The old command line options were for managing the configuration file, such as removing it, creating it, and
dumping information to it. These features are now obsolete, but the command line options are included for 
backwards compatibility. These options do not appear on the help menu and they do nothing, they are their only to
prevent usage errors. It is highly recommended that you stop using these options, and update any scripts or
implementations that use these features. These features might be removed in a later version if deemed necessary,
so be warned.

# Conclusion

This script provides a simple method to check/download/install PaperMC server updates. You can add your command to the 
beginning of your start file, to ensure that you are always running the latest server version. 
If you are hosting a server for a friend/customer, you can use this script to manage the updating process for them, 
so they don't have to.

# Changelog 

## 1.2.0

  Bug Fixes:

  - Fixed an issue where the script would always determine that an update is necessary due to a type mismatch
  - Fixed an issue in the interactive menu when selecting the build where no input would be valid, also a type mismatch

  Features Added:

  - '--no-backup' argument for disabling the backup operation
  - '-V' argument for displaying script version and exiting
  - '--server-version' argument for displaying the server version and exiting
  - '--new' argument for skipping update operations and downloading a paper jar at the given location

  Other Fixes:

  - Added grouping to argparse, so the help menu should feel less cluttered
  - Cleaned up the formatting of all docstrings
  - Changed the wording in code comments
  - Fixed many typos

## 1.1.0

  - Added command line option '-q' for quiet output
  - Fixed typos/output issues
  - Can read config files in custom locations

## 1.0.0

  - Initial version
  - Added support for reading configuration info directly from the paper versioning file
  - Removed old command line options  
  - Fixed some issues with selecting version

# Special Thanks

[devStorm](https://github.com/developStorm) - Helped with configuration file management, and offered valuable insight
into the paper versioning file.

# Pull Requests

Pull requests are welcome and encouraged!

If you have any bug fixes or changes, feel free to open a pull request.
Any changes/fixes are greatly appreciated!

# Issues/Bugs

If you have any questions on usage, or you have found a bug, please open a github issue. I would be happy to help!

If you are reporting a bug/error, be sure to include the following:

1. Description of what you were doing
2. All arguments used
3. Version/build you are trying to install
4. Version/build of the currently installed server(If you know it)
5. Fail point(If provided, should be for most cases)
6. Stack trace/error name(If provided, should be for most cases) 