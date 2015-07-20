import operator
from app.decorators.cacheable import cacheable
from app.repositories import CampusRepository
from app.support.distance import distance_on_unit_sphere

__author__ = 'fernando'

# mapping with LAT/LONG for some of the cities with campi in SC
CAMPI_LAT_LON = {
    "CBS": [-27.282778, -50.583889],
    "ARA": [-28.935, -49.485833],
    "BLN": [-26.908889, -49.072222],
    "FLO": [-27.596944, -48.548889],
    "JOI": [-26.303889, -48.845833]
}


def get_campi_key(campus, lat, lon):
    campus_lat_lon = CAMPI_LAT_LON.get(campus.name, [0, 0])
    return distance_on_unit_sphere(lat, lon, campus_lat_lon[0], campus_lat_lon[1])


def sort_campi_by_distance(filters):
    campi = filters["campi"]
    lat = filters["lat"]
    lon = filters["lon"]
    return map(
        operator.itemgetter(1),
        sorted(
            zip(
                map(
                    get_campi_key,
                    campi,
                    (lat for _ in campi),
                    (lon for _ in campi),
                ),
                campi
            ),
            key=operator.itemgetter(0)
        )
    )




@cacheable(consider_only=["semester", "_full"])
def get_campi(filters):
    repository = CampusRepository()
    full = filters.pop("_full", None)
    if filters:
        campi = repository.find_by(filters).get_result()
    else:
        campi = repository.find_all().get_result()
    if not full:
        # Avoid descompression of big data when caching
        for campus in campi:
            campus.disciplines = []
    return campi


@cacheable()
def get_campus(id_value):
    repository = CampusRepository()
    campus = repository.find_by_id(id_value).get_result()
    if campus:
        campus.disciplines = []
    return campus