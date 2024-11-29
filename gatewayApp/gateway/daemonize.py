

"""
Daemonizes the current process by performing the following steps:
1. Forks the current process and exits the parent process.
2. Changes the working directory to the root directory.
3. Creates a new session and sets the process group ID.
4. Sets the file mode creation mask to 0.
5. Forks the process again and exits the second parent process.
6. Redirects standard input, output, and error file descriptors to /dev/null.
"""

import os
import sys

def daemonize():
    """Daemonizes the current process."""
    try:
        pid = os.fork()
        if pid > 0:
            # Exit the parent process
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Fork #1 failed: {e.errno} ({e.strerror})\n")
        sys.exit(1)

    # Detach from the parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            # Exit from the second parent
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Fork #2 failed: {e.errno} ({e.strerror})\n")
        sys.exit(1)

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "r") as dev_null:
        os.dup2(dev_null.fileno(), sys.stdin.fileno())
    with open("/dev/null", "a+") as dev_null:
        os.dup2(dev_null.fileno(), sys.stdout.fileno())
        os.dup2(dev_null.fileno(), sys.stderr.fileno())
