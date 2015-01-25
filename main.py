from bottle import route, run, request
from parse_rest.connection import register
from parse_rest.datatypes import Object

import sched, time
from calendar import timegm

import threading
from threading import Thread

from apns import APNs, Payload

from twilio.rest import TwilioRestClient

register("lkHCX43bL8tqi0kpiICrOdXLlcx6yxDs3k9rUE5A", "uIE9zOF0dsbr5N9uPrtF2eBDiuGiIhuffvFsdaaA")

apns = APNs(use_sandbox=True, cert_file='TransponderCert.pem', key_file='TransponderKey_unencrypted.pem')

account_sid = "AC2d73e6a6e37a5b3bd8809db9eafb2a60"
auth_token = "b4e9be2219ad2cc986e8ab77b9874c84"
client = TwilioRestClient(account_sid, auth_token)

def timestamp():
    return timegm(time.gmtime())

class Users(Object):
    pass

s = sched.scheduler(time.time, time.sleep)

def check_db(sc):
    print("Checking database...")

    users = Users.Query.filter(onTrip=True)

    for user in users:
        minutes = ((timestamp() / 60.0) - (user.lastResponse / 60.0))
        #print(str(minutes))
        if minutes >= user.pingInterval:
            if not user.confirmationSent:
                token_hex = user.deviceToken
                payload = Payload(alert="Are you OK?", sound="default", badge=1)
                apns.gateway_server.send_notification(token_hex, payload)

                user.confirmationSent = True
                user.lastPing = timestamp()
            else:
                responseMinutes = ((timestamp() / 60.0) - (user.lastPing / 60.0))
                if responseMinutes >= 0.5:
                    contacts = user.contacts.split(",")
                    for contact in contacts:
                        message = client.messages.create(body="%s has not replied to their most recent Transponder notification. Make sure they're safe by checking their location at http://104.236.122.251/map?uid=%s" % (user.name, user.objectId), to="+%s" % (contact), from_="+19177461129")
        else:
            user.confirmationSent = False

        user.save()

    sc.enter(5, 1, check_db, (sc,))

@route('/map')
def map():
    objectId = request.query['uid']
    user = Users.Query.get(objectId=objectId)
    lat = user.latitude
    lon = user.longitude
    return """<!DOCTYPE html>
<html>
    <head>
        <style type="text/css">
            html, body, #map-canvas { height: 100%; margin: 0; padding: 0;}
        </style>
        <script type="text/javascript"
            src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCXclSUdDa_gOxSRlZ47H44uGHOoY4uZJM">
        </script>
        <script type="text/javascript">
            function initialize() {
                var coords = new google.maps.LatLng(""" + str(lat) + """,""" + str(lon) + """);

                var mapOptions = {
                    center: coords,
                    zoom: 8
                };

                var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

                var marker = new google.maps.Marker({
                        position: coords,
                        map: map,
                        title: \"""" + str(user.name) + """'s Location'\"
                });
            }
            google.maps.event.addDomListener(window, 'load', initialize);
        </script>
    </head>
    <body>
        <div id="map-canvas"></div>
    </body>
</html>"""

def start_backend():
    s.enter(5, 1, check_db, (s,))
    s.run()

def start_site():
    run(host='104.236.122.251', port=80, debug=True)

if __name__ == '__main__':
    backend = Thread(target=start_backend)
    backend.daemon = True
    backend.start()

    site = Thread(target=start_site)
    site.daemon = True
    site.start()

    while True:
        time.sleep(1)
