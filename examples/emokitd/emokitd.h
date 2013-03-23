#include "sys/stat.h"

#define DAEMON_IDENT "emokitd"
#define PIDFILE "/var/run/emokitd.pid"
#define LOCKMODE (S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH)
#define FIFO_PATH "/dev/emokitd"
#define EMOKIT_PKT_SIZE 32

#ifndef DEBUG
#define DEBUG 0
#endif
