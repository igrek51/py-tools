### watchtower

Tool for monitoring the changes in multiple files.
When any change is detected a given command is executed.

### Usage:

```
./watchtower.py [options] -f '<files>' [...] -e <command>
```

Optional arguments:

 -f, --files <file1> [<file2>] ['<pattern1>'] [...] - include masks - absolute or relative pathnames
or shell-style wildcard patterns (including recursive directories and subdirectories), which refer to files to be observed

 -x, --exclude <file1> [<file2>] ['<pattern1>'] [...] - exclude masks - filenames 
or shell-style wildcard patterns, which contains files not to be observed

 -e, --exec <command> - execute given command when any change is detected

 -i, --interval <seconds> - set interval between subsequent changes checks (default 1 s)

 --noinit - do not execute command on the initialization

 -h, --help - display this help and exit

## example patterns:
* file1
* prefix*
* 'dir1/*'
* "*.tex"
* 'dir2/*.py'
* "*"
* '**'
* '**/*.py'
* '/abs/path/*'
* '/abs/path/**'
