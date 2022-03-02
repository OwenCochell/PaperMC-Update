# Changelog 

## 2.1.0

Features Added:

  - Added a new keyword, `current`, which will automatically select the current version/build to install

Bug Fixes:

  - Removed some junk debugging messages that would appear even if we are quieted.

other Fixes:

  - Added section to the readme that describes how to use keywords.


## 2.0.0

Major changes!
Due to numerous code and feature changes,
we have bumped to version 2.
This update mostly focuses on behind the scene bug 
fixes and improvements,
but we do have some new features to offer.

Features Added:

  - Added the ability to check the integrity of the file using the SHA256 hash provided by the PaperMC API
  - Implemented a very basic caching system to reduce the number of calls made to the PaperMC API
      (Makes your network happy due to saved bandwidth, and makes you happy due to saved time).
      This may get improved in the future if necessary. 
  - Added the ability to view install data such as changelogs and hashes
  - Made determining the output filename a bit simpler, check out the readme

Bug Fixes:

  - When a filename is not specified, we install the file to the given location instead of the parent directory
  - Version checks will NOT determine an update is necessary if the currently installed version and 
      version to install is the same(This goes for builds as well)
  - Fixed bugs related to manually specifying the output filename
  - Fixed bugs were the script will not backup the jar file when necessary

Other Fixes:

  - Cleaned up the code to be more readable(Typing, better docstrings, cleaner code)
  - Made the Updater class and other components usable by third parties!
      You can import these components into your own scripts to easily communicate with the PaperMC API!
      Checkout the readme for more info on this!
  - Cleaned up the readme to be easier to read, and added sections to explain this update

## 1.4.0

Features Added:

  - Added support for the PaperMC v2 API, the usage of the script remains unchanged

## 1.3.0

  Bug Fixes:

   - Fixed huge bug where script would crash due to a missing argparse argument
   - Fixed bug where if file copy failed during install, the script would continue instead of exit

  Features added:

   - User can now specify output name of new file
   - User can now copy old file to a separate location before the update process
   - Script now uses recommended paper name if another name is not specified

  Other Fixes:

   - Added a section to the readme explaining how to handle filenames
   - Added some examples demonstrating the new command line arguments

## 1.2.1

  Bug Fixes:

   - Added a version check to the start of the script, which will exit if the python version is below 3.6
   - When checking script version with '-V', we now display the version and exit instead raising an error

  Other Fixes:

   - Added a section to the readme explaining python versions and how to manually specify them
   - Added some missing command line arguments to the readme
   - Moved '--server-version' argument to the 'version' group in argparse

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
