# PaperMC-Update
A simple CLI script for automating the checking, downloading, and installing of PaperMC server updates.
NOTE: This script can only be used for updating a [PaperMC Minecraft Server](https://papermc.io/). I highly recommend their implementation, as it is incredibly fast, supports multiple plugin formats, and is highly customisable. Consider changing if any of that sounds good to you. You can find the PaperMC documentation [Here](https://paper.readthedocs.io/en/latest/), and you can find their github page [Here](https://github.com/PaperMC).

# Prerequisites
You must have Python 3+ installed. It should come pre-installed on most systems. This script has no other dependencies, so all you need is python! Instructions for installation are below:

## Linux:

RPM:
>yum install python3.7

Or:

DEBIAN:
>apt install python 3.7
(Or use whatever packet manager is installed on your system)
## MacOS:

>brew install python 3.7

## Windows:

Windows users can download python [Here](https://www.python.org/downloads/). The installation is very straightforward, although we recommend you add python to your PATH environment variable, as this makes using python much easier.

More information on installing/configuring python can be found [Here](https://www.python.org/downloads/).
(Any python version works, although I recommend python 3.7)

# Usage

You may run the command like so:

> python server_update.py [PATH]
Where [PATH] is the path to your paperclip.jar file. More info on the paperclip.jar format can be found [Here](https://paper.readthedocs.io/en/latest/about/structure.html#id2). If a new file is downloaded, it will be installed to this path under the same name.

This command will do the following:

1. Attempt to load configuration data from the config directory(~/.server_update). The configuration data contains the currently installed server version and build. If no configuration data is found, and version info is not supplied via the command line, then the version and build for the currently installed server will default to 0.
2. Check for a new version/build using the [PaperMC download API](https://paper.readthedocs.io/en/latest/site/api.html#downloads-api).
3. If a new version/build is available, the default version and build(usually the latest) will be installed. Alternatively, the user can be prompted to manually select which version/build they want to be installed(Will occur if the '--interactive' flag is passed).
4. The selected version is downloaded to a temporary directory located somewhere on your computer(This directory is generated using the python tempfile module, meaning that it will be generated in a safe, unobtrusive manner, and will be automatically removed at termination of the script).
5. The currently installed version of the server is backed up to the temporary directory, and deleted. The newly downloaded server is moved from the temporary directory to the path of the old server, and will retain the name of the old server(If an error occurs for any reason during the instillation procedure, then the script will attempt to recover your backed up version of the old server from the temporary directory).
6. Dumps the current configuration data into the config directory(Created if it does not exsist already). This saves the currently installed version and build, so it can be automatically checked at a later execution of the script.
7.(Optional) - Deletes the config directory and all data within it. Will only occur is the user issues the '--cleanup' argument.

# Command Line Options:

The following command line options are available:

>-v [VERSION], --version [VERSION]
Sets the default value for the version to install, defaults to latest.
>-b [BUILD], --build [BUILD]
Sets the default value for the build to install, defaults to latest.
>-iv [VERSION]
Sets the currently installed server version, ignores config data.
>-ib [BUILD]
Sets the currently installed server build, ignores config data.
>-C, --cleanup
Deletes the config directory and all data within.
>-c, --check-only
Checks for an update, does not install.
>-nc, --no-check
Does not check for an update, skips to install.
>-i, --interactive
Prompts the user for the version they would like to install.
>-nlc, --no-load-config
Will not load configuration data
>-ndc, --no-dump-config
Will not dump configuration data

# Examples:

Automatically check and download the latest version of the server:
>python server_update.py [PATH]

Download and install the latest build of version 1.13.2, without checking:
>python server_update.py --no-check --version 1.13.2 [PATH]

Install latest version, regardless of server version:
>python server_update.py --no-load-config  --no-check [PATH]

Install specific version, regardless of server version:
>python server_update.py --no-load-config --no-check --version [VERSION TO INSTALL] --build [BUILD TO INSTALL] [PATH]

Interactively select a version you want to install, regardless of server version:
>python server_update.py --no-check --no-load --interactive [PATH]

Check to see if a newer version is available, does not install:
>python server_update.py --check-only [PATH]

# Conclusion

This script provides a simple method to check/download/install PaperMC server updates. You can add your command to the start of your startfile, to ensure that you are always running the latest version. If you are hosting a server for a freind/customer, you can use this script to manage the updating process for them, so they don't have to.

# Issues/Bugs

If you have any questions on usage, or you have found a bug, please open a github issue. I would be happy to help!
