
Creepers Default Start String:
Python C:\Minecraft\server_update.py --user-agent "PaperUpdater/3.0.1 (github.com/creeper36)" --batch --no-backup C:\Minecraft\paper.jar

# PaperMC-Update

A simple CLI script that can check, download, and install PaperMC jar files.

NOTE: This script can only be used for updating a [PaperMC Minecraft Server](https://papermc.io/). I highly recommend 
their implementation, as it is incredibly fast, supports multiple plugin formats, and is highly customizable. 
Consider switching if any of that sounds good to you. 
Check out the [PaperMC Documentation](https://paper.readthedocs.io/en/latest/), 
[Download Page](https://papermc.io/downloads), and [GitHub](https://github.com/PaperMC).

# Prerequisites

You must have Python 3.7+ installed. It should come pre-installed on most linux systems. 
This script has no other dependencies, so all you need is python!

## Windows

Windows users can download python [here](https://www.python.org/downloads/windows/). The installation is very straightforward, 
although we recommend you add python to your PATH environment variable, as this makes using python much easier.

More information on installing/configuring python can be found [here](https://www.python.org/downloads/)
(Any python 3.7+ version works, although I recommend the latest version).

We also supply windows binaries that can be ran directly on windows systems without python!
We use [PyInstaller](https://www.pyinstaller.org/) to build these binaries, and they are built using the one file option, or '-F'.

These binaries are much slower than running via python, and there might be some weird bugs or quirks.
They are built for windows only. We provide one with each version change.

Sometimes, these binaries are flagged as malicious programs(usually some form of trojan)
bu numerous antivirus engines, sometimes including windows defender.
This is unfortunately quite common for freezed python binaries.
The best way to deal with the issue is to whitelist the executable in your antivirus. 

Find them [in the releases](https://github.com/Owen-Cochell/PaperMC-Update/releases)!

## MacOS

MacOS users can download python [here](https://www.python.org/downloads/mac-osx/).

Again, the installation is very straightforward, but more information can be found [here](https://docs.python.org/3/using/mac.html).

## Linux

Please refer to your distribution's package manager for installing python.

# Note on Python Versions:

In some systems, the 'python' command may point to an older version of python.
As stated above, we require python 3.7 or above, so it may be necessary to manually specify the python version to use.

This can be done like so:

>python[VERSION] script_to_run.py

Using this template, we can run python 3.9 like this:

>python3.9 script_to_run.py

This usage is most prevalent on linux devices,
as they may have older versions of python installed for compatibility reasons.

To find the version of python your command points to, you can check it's version:

>python --version

If it is below 3.7, then you will have to manually specify the version to run!

From this point on, we will use the default 'python' command in our examples,
assuming that it's a valid python version.
Be sure to specify your python version if necessary!

# Usage

You may run the script like so:

> python server_update.py [PATH]

Where [PATH] is the path to your paperclip.jar file.
By default, when a new file is downloaded, 
it will be installed to this path under the same name.

This command will do the following:

1. Attempt to load current paper version/build(`/PATH_TO_SERVER_JAR/version_history.json`, or elsewhere if specified. 
This script only supports official builds of the paper server, meaning that we may fail to read config 
information for un-official builds). If no configuration data is found, and version info is not supplied via the 
command line, then the version and build for the currently installed server will default to 0.
2. Check for a new version/build using the 
[PaperMC download API](https://docs.papermc.io/misc/downloads-api).
3. If a new version/build is available, the default version and build(usually the latest) will be installed.
If you wish to select a version/build to install, then you can use '--version' and '--build' arguments to specify this. 
Alternatively, the user can be prompted to manually select which version/build they want to be installed. You can use 
the `--interactive` flag for this.
4. The selected version is downloaded to a temporary directory located somewhere on your computer
(This directory is generated using the python tempfile module, meaning that it will be generated in a safe, 
unobtrusive manner, and will be automatically removed at termination of the script).

    If the version selected has no available builds, then the script will print a warning and exit.
5. The integrity of the file will be checked using the SHA256 hash provided by the PaperMC API.
If this check fails, the install will cancel.
6. The currently installed version of the server is backed up to the temporary directory, and deleted.
This option can be disabled if you so choose.
7. The newly downloaded server jar is moved from the temporary directory to the path of the old server, 
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

Specifies the output name of the new file:
>-o [NAME], --output [NAME]

Checks for an update, does not install:
>-c, --check-only

Does not check for an update, skips to install:
>-nc, --no-check

Prompts the user for the version they would like to install:
>-i, --interactive

Will not load configuration data:
>-nlc, --no-load-config

Sets config file path(`/PATH_TO_SERVER_JAR/version_history.json` by default):
>-cf [CONFIG PATH], --config-file [CONFIG PATH]

Disables the backup feature:
>-nb, --no-backup

Disables the file integrity check:
>-ni, --no-integrity

Copies the old jar file to a new location before deletion:
>-co, --copy-old

Installs a new paper jar to the specified location:
>-n, --new

Displays script version information:
>-V, --script-version

Displays server version, extracted from configuration file:
>-sv, --server-version

Will only output errors and interactive questions to the terminal:
>-q, --quiet

Copies the old file to a new location before the installation process:
>-co [PATH], --copy-old [PATH]

Displays stats on the selected version and build:
>-s, --stats

Specifies a custom user agent string, see below for why you should do this and what value you should choose:
>-ua [AGENT], --user-agent [AGENT]

Log-friendly filtering of output mainly used for batch files.
>-ba, --batch

Checks GitHub for a new version of this script, and upgrades if necessary:
>-u, --upgrade

## User Agent

According to the new [API V3 documentation](https://docs.papermc.io/misc/downloads-api),
it is **REQUIRED** to specify a custom user agent string.
This string must:

- Clearly identify your software or company
- Not be generic (defaults from curl, wget, ect.)
- Includes a contact URL or email address (homepage, bot info page, support email, etc.)

Some examples:

```
--user-agent "PaperUpdater/3.0.1 (johnsmith@email.com)"
-ua paperupdater-github.com/johnsmith
```

If you add a space in your string it will fail unless you add quotes.. The fail will think its the next argument.
If you fail to provide a -UA argument it will not fail because the dev (Owen Cochell) is using his default as a work-around.
YOU NEED TO CHANGE IT TO COMPLY WITH THESE NEW API RULES.

These requirements were pulled directly from the documentation page linked above,
but they may change at any time. Please check the page regularly to ensure you are in compliance!

You may use the user agent option (`-ua [AGENT], --user-agent [AGENT]`) to specify this value.
It is optional, but **HIGHLY** recommended to set this value to something custom.
If a custom user agent is not provided, then this script will use the default value:

```
PaperMC-Update/VERSION (https://github.com/OwenCochell/PaperMC-Update)
```

(Where `VERSION` is the current version of this script)

This default value may be blocked at any time at the discretion of the PaperMC team!
Which means, if you do not specify a custom user agent, then this script may stop working!
In addition, this value will NOT change going forward (with the exception of the `VERSION` component).
To avoid any future problems, you should, again, use a custom user agent!

## Special Keywords

The `-v`, `-b`, and interactive menu have special keywords
that can be used to do special things.

The `latest` keyword will automatically select the latest option available.

The `current` keyword will automatically select the currently installed value.

For example, lets say you have paper version 1.17 and build 60 installed.
If you want to get the latest build while maintaining your installed version,
then you can run server update like so:

>python server_update.py -v current [PATH]

This will only install new builds for your current version.
You can also use the `current` keyword to ensure that the version
will never change, regardless of what you have installed.

These keywords can be used in the interactive menu as well.
You can also use these keywords for selecting the build,
although using the `current` keyword for build selection is not recommended! 

## Upgrading the Script

This script has the ability to upgrade itself!
You can do this by providing the `-u` parameter.

We do this by checking GitHub for any version changes.
If there is a change, then we download the new file
and replace the currently running script with the new one.
If we are upgrading, then we will immediately exit after the operation,
and no other actions will be done.

Please note, this upgrade operation is not compatible 
with prebuilt binaries!
If you attempt to upgrade a pre-built binary,
then the script will print a warning and exit.

## Deprecated Command Line Options

The following command line options are deprecated. They are still included for backwards compatibility,
but they do nothing and should not be used.

Delete the config directory and all data within:
>-C, --cleanup

Will not dump configuration data:
>-ndc, --no-dump-config

Specify which config directory should be used, defaults to `/DIR_OF_YOUR_SERVER_JAR_FILE/server_update`:
>--config [PATH]

Does not rename the new jar file:
>-nr, --no-rename

# Note on filenames:

We have a couple ways of specifying the target and output filenames.
In these examples, 'old file' is the jar file that is currently installed.
'New file' is the new file jar file that is being installed in its place.

In these coming examples, lets say you have a jar file you want to update located here:
>minecraft/paper.jar

## The Best Way:

The easy way to tell the script where the file to update is located is to pass the path to said file, like so:
>python server_update.py minecraft/paper.jar

In this example, the old file will be backed up and deleted.
When the new file is downloaded,
it will be renamed to 'paper.jar' and moved to the directory the old file was in,
effectively replacing it.

This is the recommended way to specify filenames!
Specifying the path to the jar file to update will allow the script to 
automatically backup, move, and delete your files for you.
It also ensures that no matter the version or operations done to the target file,
it will always have the same name.

## Custom Output Names:

You can also specify a custom name of the new file like so:
>python server_update.py -o new_file.jar minecraft/paper.jar

This will do the same as the example above, 
but instead of the new file retaining the old name,
it will be renamed to the value you specified.

In our example, the old file will be backed up and deleted as usual,
but the new file will be renamed to 'new_file.jar',
and moved to the directory the old file was in.

## Keeping Old File:

You can use the '--copy-old' parameter
to specify where you want the old file to be copied to.

Using the example from above:
>python server_update.py --copy-old paper_old.jar minecraft/paper.jar

The old file will still be deleted,
but a copy of it will be saved to 'paper_old.jar'.

You can also specify a path like this:
>python server_update.py --copy-old /new/path/file.jar minecraft/paper.jar

In this example, the old file is copied to '/new/path/file.jar'
before the installation operation.

These options will be ignored if there is no target file!

Be warned, that the old file will overwrite any files in the copy location
that share the same name!

## Other Filename Stuff:

If no target filename is specified from the path,
and no output filename is specified,
then the default filename will be used.
The default name usually looks something like this:
>paper-[VERSION]-[BUILD].jar

So, if you downloaded build 734 version 1.16.5:
>paper-1.16.5-734.jar

You can specify a directory to target instead of a file like this:
>python server_update.py minecraft/

This will automatically disable old file deletion and backup.
The newly downloaded file will simply be moved to the target directory,
and will not be renamed(unless otherwise instructed by the '-o' parameter).


## Errorlevels:  
After paper.jar has an update it will Exit in a Normal state with Errorlevel 8.
This can be used by batch files to trigger 'GOTO UPDATE-FOUND' in the batch script.   

Current Errorlevels Supported :   
0 - Normal Exit- No MC Update   
8 - Normal Exit- New Paper Was Found and Updated

        PYTHON server_update.py C:\Minecraft\paper.jar
        IF %ERRORLEVEL% EQU 8 GOTO NEWPAPERFOUND
        GOTO SAMEPAPER


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

Display stats on version 1.16.5 build 432 before installation if update is available:
>python server_update.py --stats --version 1.16.5 --build 432 [PATH]

Display stats on version 1.16.5 build 432 without installing anything:
>python server_update.py --stats --version 1.16.5, --build 432 -c -nc

Install a paper jar at the given location, without going through the update process.
Great if you want to set up a new server install.
>python server_update.py --new -o paper.jar [PATH]

Copy the old file to a new location before the installation process:
>python server_update.py --copy-old /new/spot/old.jar [PATH]

Select the currently installed version as the version to install:
>python server_update.py -v current [PATH]

Upgrades the script if necessary:
>python server_upgrade.py -u

# Notes on Deprecated Features

In earlier versions of PaperMC-Update, the script would keep a config file in the users home directory
(Or elsewhere if specified) containing version information on the server so it can be persistent across runs.

There were many problems with this: it created unnecessary files, it was inaccurate,
and it made using PaperMC-Update a lot more complicated. Now, we read version info from a file named
'version_history.json', which is kept in the root directory of the server, and is managed by the server itself. This
eliminates the need for 'script-generated configuration files',
and makes PaperMC-Update easier to use and more accurate.

However, there are some things to keep in mind:

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
backwards compatibility. These options do not appear on the help menu and they do nothing. This is to prevent usage errors. It is highly recommended that you stop using these options, and update any scripts or
implementations that use these features. These features might be removed in a later version if deemed necessary, so be warned.

# Updater Class:

Developers can import the Updater class into their own projects.
The updater class offers entry points into the PaperMC API,
and allows users to get version/build data
and download jar files.

You can import and create the class like so:

```python
from server_update import Update

update = Update()
```

Just be sure the server_update.py file is present in the directory
of the code importing it.

You should have a look at the docstrings in the source code for usage.
All arguments and outputs are described and typed,
so implementing the Updater class into your code should be relatively painless.

# Conclusion

This script provides a simple method to check/download/install PaperMC server updates. You can add your command to the 
beginning of your start file, to ensure that you are always running the latest server version.
If you are hosting a server for a friend/customer, you can use this script to manage the update/install process for them, 
so they don't have to.

# Changelog

The changelog has moved to CHANGELOG.md.
All current and future changes will be kept in that location.

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
