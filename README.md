
---

# File Cleaning and Organizing Tool

A Python-based tool for cleaning and organizing files within one or more directories. This tool uses only built-in modules and is designed to detect and manage issues such as empty files, temporary files, duplicate files, files with identical names (but different modification times), files with problematic characters in their names, and files with non-standard permissions.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Modes and Examples](#modes-and-examples)
    - [Empty Files](#empty-files)
    - [Temporary Files](#temporary-files)
    - [Duplicate Files](#duplicate-files)
    - [Same-Name Files](#same-name-files)
    - [File Attributes](#file-attributes)
    - [Problematic File Names](#problematic-file-names)
    - [Running All Operations](#running-all-operations)
- [Test Directory Generation](#test-directory-generation)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Introduction

Managing large collections of files scattered over multiple directories can be challenging—especially when issues like duplicates, empty files, and inconsistent naming or permissions occur. This tool provides a simple, interactive way to identify and clean up such issues.

The script is organized into two primary classes:
- **ArgParser**: Handles all command-line argument parsing.
- **FileCleaner**: Encapsulates file cleaning operations, including deletion, renaming, permission changes, and duplicate detection.

## Features

- **Empty Files**: Identify and optionally delete empty files.
- **Temporary Files**: Detect and remove files with temporary extensions (e.g., `.tmp`, `~`).
- **Duplicate Files**: Locate duplicate files (based on MD5 hash) and keep only the oldest version.
- **Same-Name Files**: Identify files with the same name across directories and retain only the newest version.
- **File Attributes**: Check and adjust file permissions to a desired mode.
- **Problematic File Names**: Detect file names with problematic characters (e.g., `:`, `?`, `*`) and offer to rename them using a substitute character.

## Requirements

- **Python 3.x**: Ensure you have Python 3 installed.
- **Operating System**: Unix-like systems are recommended (due to permission handling), though the script can also run on Windows with some limitations.

## Installation

1. **Clone or Download the Repository:**

   ```bash
   git clone https://github.com/yourusername/file-cleaner.git
   ```

   Or download the ZIP and extract it.

2. **Verify Python Version:**

   ```bash
   python3 --version
   ```

3. **(Optional) Make the Script Executable:**

   ```bash
   chmod +x clean_files.py
   ```

## Configuration

The tool reads its configuration from a file at `$HOME/.clean_files`. If this file does not exist, default values are used.

Example configuration (`~/.clean_files`):

```ini
desired_mode=rw-r--r--
problematic_chars=:\".;*?$#'|\
substitute_char=.
temp_extensions=.tmp,~
```

- **desired_mode**: Target permission mode for files (symbolic format).
- **problematic_chars**: Characters in file names that may cause issues.
- **substitute_char**: The character to replace problematic characters.
- **temp_extensions**: Comma-separated list of file extensions considered temporary.

## Usage

The tool accepts two positional arguments:

1. **mode** (optional): Specifies which cleaning operation to perform.
   - Allowed modes: `empty`, `temp`, `dups`, `same`, `attrib`, `rename`
   - If omitted (or an empty string is provided), all operations are executed.

2. **directories** (required): One or more directories to process.

### Command-Line Arguments

The built-in `ArgParser` class encapsulates the command-line parsing using Python’s `argparse` module. For example, to run the tool on a directory called `test_dir` in duplicate mode, you would use:

```bash
python clean_files.py dups test_dir
```

### Modes and Examples

#### Empty Files

Find and process empty files:

```bash
python clean_files.py empty test_dir
```

*Expected prompt:*
```
Empty file: /path/to/test_dir/subdir1/empty.txt
Delete? (y - yes, n - no, a - always delete):
```

#### Temporary Files

Find temporary files (based on extensions):

```bash
python clean_files.py temp test_dir
```

*Expected prompt:*
```
Temporary file: /path/to/test_dir/subdir1/temp_file.tmp
Delete? (y - yes, n - no, a - always delete):
```

#### Duplicate Files

Detect duplicates (using MD5 hash) and delete extra copies:

```bash
python clean_files.py dups test_dir
```

*Expected prompt:*
```
Duplicates found for file (oldest retained): /path/to/test_dir/subdir1/duplicate.txt
Copy: /path/to/test_dir/subdir2/duplicate_copy.txt (mtime: 1623456789)
Delete this copy? (y - yes, n - no, a - always delete):
```

#### Same-Name Files

Identify files with the same name across directories:

```bash
python clean_files.py same test_dir
```

*Expected prompt:*
```
Files with name: same.txt
Retained version (newest): /path/to/test_dir/subdir2/same.txt
Older version: /path/to/test_dir/subdir1/same.txt (mtime: 1623456780)
Delete this older version? (y - yes, n - no, a - always delete):
```

#### File Attributes

Check file permissions and adjust to the desired mode:

```bash
python clean_files.py attrib test_dir
```

*Expected prompt:*
```
File: /path/to/test_dir/bad_permissions.txt
Current permissions: 0o777 Expected: 0o644
Change permissions? (y - yes, n - no, a - always change):
```

#### Problematic File Names

Find and rename files with problematic characters:

```bash
python clean_files.py rename test_dir
```

*Expected prompt:*
```
File with problematic name: /path/to/test_dir/problematic:file?name.txt
Proposed new name: /path/to/test_dir/problematic.file.name.txt
Rename? (y - yes, n - no, a - always rename):
```

#### Running All Operations

To run **all operations** sequentially, provide an empty string as the mode:

```bash
python clean_files.py "" test_dir
```

This will execute empty file deletion, temporary file cleanup, duplicate file detection, same-name file processing, permission adjustments, and file renaming in one run.

## Test Directory Generation

A helper script, `create_test_dir.py`, is provided to generate a sample test directory structure with files covering all functionalities.

### Steps:

1. **Save the following script as `create_test_dir.py`:**

   ```python
   import os
   import time

   def create_test_structure(base_dir="test_dir"):
       """
       Creates a test directory structure with files for testing the cleaning script.
       
       The structure includes:
         - An empty file.
         - A temporary file (.tmp).
         - Duplicate files with identical content.
         - Files with the same name but different modification times.
         - A file with problematic characters in its name.
         - A file with non-standard permissions.
       """
       os.makedirs(base_dir, exist_ok=True)
       subdirs = ["subdir1", "subdir2"]
       for sub in subdirs:
           os.makedirs(os.path.join(base_dir, sub), exist_ok=True)
       
       # 1. Create an empty file in subdir1
       empty_file = os.path.join(base_dir, "subdir1", "empty.txt")
       with open(empty_file, "w") as f:
           pass

       # 2. Create a temporary file (.tmp) in subdir1
       temp_file = os.path.join(base_dir, "subdir1", "temp_file.tmp")
       with open(temp_file, "w") as f:
           f.write("This is a temporary file.")

       # 3. Create duplicate files (same content, different locations)
       duplicate_content = "This is duplicate content."
       dup_file1 = os.path.join(base_dir, "subdir1", "duplicate.txt")
       dup_file2 = os.path.join(base_dir, "subdir2", "duplicate_copy.txt")
       with open(dup_file1, "w") as f:
           f.write(duplicate_content)
       with open(dup_file2, "w") as f:
           f.write(duplicate_content)

       # 4. Create files with the same name in subdir1 and subdir2 with different modification times
       same_name1 = os.path.join(base_dir, "subdir1", "same.txt")
       same_name2 = os.path.join(base_dir, "subdir2", "same.txt")
       with open(same_name1, "w") as f:
           f.write("Version 1: older content.")
       time.sleep(1)
       with open(same_name2, "w") as f:
           f.write("Version 2: newer content.")

       # 5. Create a file with problematic characters in its name in the base directory
       problematic_file = os.path.join(base_dir, "problematic:file?name.txt")
       with open(problematic_file, "w") as f:
           f.write("File with problematic characters in its name.")

       # 6. Create a file with non-standard permissions (e.g., 0777 instead of the desired 0644)
       perm_file = os.path.join(base_dir, "bad_permissions.txt")
       with open(perm_file, "w") as f:
           f.write("This file has non-standard permissions.")
       os.chmod(perm_file, 0o777)

       print("Test directory structure created in:", os.path.abspath(base_dir))

   if __name__ == "__main__":
       create_test_structure()
   ```

2. **Run the test generator:**

   ```bash
   python create_test_dir.py
   ```

   This will create a directory named `test_dir` with the following structure:

   ```
   test_dir/
   ├── bad_permissions.txt
   ├── problematic:file?name.txt
   ├── subdir1/
   │   ├── empty.txt
   │   ├── temp_file.tmp
   │   ├── duplicate.txt
   │   └── same.txt
   └── subdir2/
       ├── duplicate_copy.txt
       └── same.txt
   ```

## Troubleshooting

- **Permission Issues:**  
  If you encounter permission errors (e.g., when deleting or modifying files), ensure you have the required privileges. You might need to run the script as an administrator or with `sudo` on Unix-like systems.

- **Configuration Problems:**  
  Verify that your `~/.clean_files` file is correctly formatted (using `key=value` pairs) and contains valid values.

- **Interactive Prompts:**  
  This tool is interactive. If you are running it in an environment that does not support interactive input, try running the script directly in a terminal.