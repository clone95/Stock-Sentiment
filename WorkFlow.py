from NewsUpdater import NewsUpdater
from MongOps import connect, clear_db

a = NewsUpdater()
a.update_db()
