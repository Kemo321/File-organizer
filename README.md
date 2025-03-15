
---

# File Cleaning and Organizing Tool


## Features

- **Empty Files**: Detects and removes files with zero size.
- **Temporary Files**: Identifies and deletes files with user-defined temporary extensions.
- **Duplicates**: Finds and removes duplicate files based on content (MD5 hash), keeping the oldest version.
- **Same Name Files**: Locates files with identical names across directories, keeping the newest and offering to delete older versions.
- **File Attributes**: Checks and corrects file permissions to a specified mode.
- **Rename Files**: Renames files with problematic characters, replacing them with a substitute character.

## Usage

Run the tool using this command:

```bash
python clean_files.py [mode] directory1 [directory2 ...]
```

- **`mode`** (optional): Specifies the operation to perform. If omitted, all operations run by default. Options:
  - `empty`: Remove empty files.
  - `temp`: Remove temporary files.
  - `dups`: Remove duplicate files.
  - `same`: Remove older files with the same name.
  - `attrib`: Correct file permissions.
  - `rename`: Rename files with problematic characters.
  - `all`: Execute all operations (default if no mode is specified).
- **`directory1 [directory2 ...]`**: One or more directories to process.

### Examples

1. **Remove empty files from a directory**:
   ```bash
   python clean_files.py empty mydir
   ```

2. **Run all operations on multiple directories**:
   ```bash
   python clean_files.py dir1 dir2
   ```
   or
   ```bash
   python clean_files.py all dir1 dir2
   ```

## Configuration

The tool reads settings from a `.clean_files` file in the current working directory. If absent or invalid, it falls back to defaults. The file uses a key-value format (`key=value`).

Supported options:
- **`desired_mode`**: File permission mode in symbolic notation (e.g., `rw-r--r--` for owner read/write, others read). Default: `rw-r--r--` (octal `0644`).
- **`problematic_chars`**: Characters flagged as problematic in filenames. Default: `:".;*?$#'|\`.
- **`substitute_char`**: Replacement character for problematic characters. Default: `.`.
- **`temp_extensions`**: Comma-separated list of temporary file extensions. Default: `.tmp,~`.

**Example `.clean_files`**:
```
desired_mode=rw-r--r--
problematic_chars=:".;*?$#'|\
substitute_char=_
temp_extensions=.tmp,.temp,~
```

## Operations Details

- **Empty Files**: Finds files with zero bytes and prompts for deletion.
- **Temporary Files**: Targets files with extensions from `temp_extensions` and prompts for deletion.
- **Duplicates**: Uses MD5 hashing to detect identical content, sorts by modification time, keeps the oldest, and prompts to delete newer duplicates.
- **Same Name Files**: Groups files by name across directories, sorts by modification time, keeps the newest, and prompts to delete older ones.
- **File Attributes**: Compares permissions to `desired_mode` and prompts to adjust mismatches.
- **Rename Files**: Identifies filenames with `problematic_chars` and prompts to rename using `substitute_char`.

## Interactive Prompts

For each file matching an operation’s criteria, the tool asks for input:
- **`y`**: Yes, perform the action (e.g., delete, rename).
- **`n`**: No, skip this file.
- **`a`**: Always perform the action for all similar files without further prompts.

**Example**: Choosing `a` when deleting empty files will remove all empty files automatically.

## Testing the Tool

A helper script, `create_test_structure.py`, sets up a test environment:

```bash
python create_test_structure.py
```

This generates a `test_dir` containing:
- Empty file (`empty.txt`).
- Temporary file (`temp_file.tmp`).
- Duplicate files (`duplicate.txt`, `duplicate_copy.txt`).
- Same-name files (`same.txt` in subdirectories with varying times).
- Problematic filename (`problematic:file?name.txt`).
- File with odd permissions (`bad_permissions.txt`, mode `0777`).

Test the tool with:
```bash
python clean_files.py test_dir
```

## Dependencies

The tool uses only Python standard libraries (`os`, `sys`, `hashlib`, `argparse`), requiring no external packages.

## Notes

- **Recursive**: Processes directories and subdirectories via `os.walk`.
- **Time-Based**: Uses modification times (`st_mtime`) to determine oldest/newest files.
- **Limitations**: Ignores symbolic links and special files (e.g., sockets).
- **Permissions**: Requires read/write access to files and directories to function properly.

---
