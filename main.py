from bottle import route, run, request
from parse_rest.connection import register
from parse_rest.datatypes import Object

import sched, time
from calendar import timegm

from apns import APNs, Payload

apns = APNs(use_sandbox=True, cert_file='TransponderCert.pem', key_file='TransponderKey_unencrypted.pem')

def timestamp():
    return timegm(time.gmtime())

register("lkHCX43bL8tqi0kpiICrOdXLlcx6yxDs3k9rUE5A", "uIE9zOF0dsbr5N9uPrtF2eBDiuGiIhuffvFsdaaA")

class Users(Object):
    pass

s = sched.scheduler(time.time, time.sleep)

def check_db(sc):
    print("Checking database...")

    users = Users.Query.filter(onTrip=True)

    for user in users:
        minutes = ((timestamp() / 60.0) - (user.lastResponse / 60.0))
        print(str(minutes))
        if minutes >= user.pingInterval:
            if not user.confirmationSent:
                token_hex = user.deviceToken
                payload = Payload(alert="Are you OK?", sound="default", badge=1)
                apns.gateway_server.send_notification(token_hex, payload)

                user.confirmationSent = True
        else:
            user.confirmationSent = False

        user.save()

    sc.enter(30, 1, check_db, (sc,))

s.enter(30, 1, check_db, (s,))
s.run()

@route('/map')
def map():
    objectId = request.query['rid']
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
                        title: \"""" + str(user.lastPing) + """'s Location'\"
                });
            }
            google.maps.event.addDomListener(window, 'load', initialize);
        </script>
    </head>
    <body>
        <div id="map-canvas"></div>
    </body>
</html>"""

run(host='104.236.122.251', port=80, debug=True)
