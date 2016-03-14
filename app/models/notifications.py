from gcm import GCM
from app import webapp
from app import mysql 
import json
from app.decorators import async
from app.models import Utils

class Notifications():
    def __init__(self, gcm_id=''):
        self.gcm_id = gcm_id.split(",") if gcm_id else 0
        self.gcm = GCM(webapp.config['GCM_API_KEY'])
        self.is_enabled = webapp.config['NOTIFICATIONS_ENABLED']

    def sendNotification(self, data):
        data['bottom_text'] = "Ostrich Books"
        if self.is_enabled and self.gcm_id:
            notification_status = self.gcm.json_request(registration_ids=self.gcm_id, data=data)
            return notification_status

    @async
    def startDataUpdate(self):
        if self.gcm_id:
            self.gcm.json_request(registration_ids=self.gcm_id, data={'notification_id': 99})
            return
        self.sendMassNotification({'notification_id': 99})

    @async
    def sendMassNotification(self, notification_data, admin=0):
        if admin:
            admins = ",".join([str(_) for _ in Utils.getAdmins()])
            query_condition = " WHERE user_id in ("+admins+")"
        else:
            query_condition = ""

        cursor = mysql.connect().cursor()

        cursor.execute("""SELECT gcm_id FROM users"""+query_condition
                +""" UNION SELECT gcm_id FROM users_unregistered""")
        all_gcm = cursor.fetchall()
        all_gcm_ids = []
        for gcm in all_gcm:
            all_gcm_ids.append(gcm[0])
        self.gcm.json_request(registration_ids=all_gcm_ids, data=notification_data)


