import folium
from shapely.geometry import mapping, Polygon, MultiPolygon, Point
import folium
import openrouteservice as ors

from dirs import BASE_PATH


def get_map(start, end, avoid_area_extension_point=None, return_summary=False):
    if avoid_area_extension_point:
        planner.add_avoid_area(avoid_area_extension_point, scale_hundred_m=1)
    route = planner.get_route(start, end, "driving-car")
    m = planner.create_map(route, start, end)
    if return_summary:
        summary = route['features'][0]['properties']['summary']
        summary["segments_num"] = len(
            route['features'][0]['properties']['segments'][0]['steps']
            )
        return m, summary
    else:
        return m

class RoutePlanner:
    def __init__(self, credentials_path, avoid_features=None):
        
        self.avoid_areas = []
        self.avoid_features = avoid_features
        with open(credentials_path, "r") as f:
            token = f.read()
        self.client = ors.Client(key=token)


    def get_route(self, start_point, end_point, profile='foot-walking'):
        coordinates = [start_point, end_point]
        options = {}
        
        if self.avoid_features:
            options["avoid_features"] = self.avoid_features
        
        if self.avoid_areas:
            avoid_polygons_geojson = mapping(MultiPolygon(self.avoid_areas))
            options["avoid_polygons"] = avoid_polygons_geojson

        route = self.client.directions(
            coordinates=coordinates,
            profile=profile,
            format='geojson',
            options=options if options else None,
            validate=False
        )

        return route

    def create_map(self, route, start_point, end_point, zoom_start=12):
        m = folium.Map(
            location=[
                (start_point[1] + end_point[1]) / 2, 
                (start_point[0] + end_point[0]) / 2],
            tiles='cartodbpositron', 
            zoom_start=zoom_start
        )

        
        folium.PolyLine(
            locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
            color="blue",
            weight=3,
            opacity=0.7
        ).add_to(m)

        folium.Marker(location=list(reversed(start_point))).add_to(m)
        folium.Marker(location=list(reversed(end_point))).add_to(m)

        for area in self.avoid_areas:
            folium.Polygon(
                locations=[list(reversed(coord)) for coord in area.exterior.coords],
                color='#ff7800',
                fill_color='#ff7800',
                fill_opacity=0.2,
                weight=2
            ).add_to(m)
        
        return m

    def get_route_elevation(self, route):
        polyline = route['features'][0]['geometry']['coordinates']
        elevation_data = self.client.elevation_line(
            format_in='polyline',
            format_out='geojson',
            geometry=polyline
        )
        return elevation_data['geometry']['coordinates']

    def _get_avoid_area(self, point, scale_hundred_m=1):
        radius_hundred_m = 1 / 1110 * scale_hundred_m

        #circle = center_point.buffer(radius_hundred_m)

        circle_highres = Point(point).buffer(radius_hundred_m, resolution=128)

        return circle_highres

    def add_avoid_area(self, point, scale_hundred_m=1):
        avoid_area = self._get_avoid_area(Point(point), scale_hundred_m)
        self.avoid_areas.append(avoid_area)

start = [-1.3835884, 50.8951872]
end = [-1.371837, 50.897193]


def update_m(planner, route):
    global m
    planner.create_map(route, start, end)

planner = RoutePlanner(BASE_PATH / ".creds/.osmcredentials")
route = planner.get_route(start, end)
m = planner.create_map(route, start, end)

# route = planner.get_route(start, end)
# planner.add_avoid_area((-1.380651, 50.896138), scale_hundred_m=1)
# planner.add_avoid_area((-1.378108, 50.893093), scale_hundred_m=0.5)
# route = planner.get_route(start, end)
# m = planner.create_map(route, start, end)

