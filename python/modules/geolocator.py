from geopy.geocoders import Nominatim
@anvil.server.callable
def get_coord(name):
    gc = Nominatim(user_agent="test")
    location = gc.geocode(name)
    return location.latitude, location.longitude