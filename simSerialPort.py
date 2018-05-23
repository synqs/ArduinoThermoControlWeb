import os, pty
master, slave = pty.openpty()
s_name = os.ttyname(slave)
print(s_name)
