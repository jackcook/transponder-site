from bottle import route, run, request
from parse_rest.connection import register
from parse_rest.datatypes import Object

register("lkHCX43bL8tqi0kpiICrOdXLlcx6yxDs3k9rUE5A", "uIE9zOF0dsbr5N9uPrtF2eBDiuGiIhuffvFsdaaA")

class Users(Object):
  pass

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
            title: \"""" + str(user.phoneNumber) + """'s Location'\"
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
