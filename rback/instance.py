import time
import os
import pipes


def db_back_up():
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_USER_PASSWORD = 'root'
    DB_NAME = 'test100'
    BACKUP_PATH = 'dbbackup'

    DATETIME = time.strftime('%Y-%m-%d-%H%M%S')
    TODAYBACKUPPATH = BACKUP_PATH

    if not os.path.exists(TODAYBACKUPPATH):
        os.mkdir(BACKUP_PATH)

    db = DB_NAME
    dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + DATETIME + ".sql"
    os.system(dumpcmd)
    gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + DATETIME + ".sql"
    os.system(gzipcmd)