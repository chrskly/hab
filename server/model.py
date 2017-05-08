
import web

db = web.database(dbn='mysql', db='hab', user='hab', pw='habpass')

def get_latest_telemetry():
    return db.select('telemetry', order='dt DESC', limit=1)
