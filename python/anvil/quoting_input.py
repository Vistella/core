from ._anvil_designer import landingpageTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

class landingpage(landingpageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    map = GoogleMap()
    map.center = GoogleMap.LatLng(52.2053, 0.1218)
    map.zoom = 13

  def button_1_click(self, **event_args):
    results = GoogleMap.geocode(address="Cambridge, UK")
    m = Marker(position=results[0].geometry.location)
    self.map_1.add_component(m)
    

  def submit_coord_click(self, **event_args):
    """This method is called when the button is clicked"""
    if len(self.address.text) > 0:
      lat, lon = anvil.server.call("get_coord", self.address.text)
      self.map_1.center = GoogleMap.LatLng(lat, lon)
      self.latitude.text = lat
      self.longitude.text = lon
    else:
      self.map_1.center = GoogleMap.LatLng(self.latitude.text, self.longitude.text)
    self.map_1.max_zoom = 23
    self.map_1.zoom = 16
    kWh, revenue = anvil.server.call("output", float(self.area.text))
    self.results.text = ("Energy Output per Year: {:,.2f} MWh".format(kWh/1000))

