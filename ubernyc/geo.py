import json

def read_geojson(path):
    return json.load(open(path))

def compute_centroids(shp):
    for feature in shp['features']:
        
        # compute bounding box for feature
        xs = []
        ys = []
        for coord in feature['geometry']['coordinates'][0][0]:
            xs.append(coord[1])
            ys.append(coord[0])
        x1 = min(xs)
        y1 = min(ys)
        x2 = max(xs)
        y2 = max(ys)

        # extract properties
        props = feature.pop('properties',{})

        # include centroid
        props['centroid'] = calc_centroid(x1, y1, x2, y2)
        yield props

def calc_centroid(x1, y1, x2, y2):
    """
    Given a bounding box, compute centroid
    """
    x = x1 + ((x2 - x1) / 2.0)
    y = y1 + ((y2 - y1) / 2.0)
    return [x, y]

def compute_trips(centroids):
    """
    For each neighborhood, get a price estimate for travelling to all other neighborhoods
    """
    coords = []
    for i, hood in enumerate(neighborhoods):
        if hood['boroname'] in INCLUDE_BOROS:
            candidates = copy.copy(neighborhoods)
            del candidates[i]
            hood_coords = []
            for candidate in candidates:
                yield {
                    'from': hood, 
                    'to': candidate, 
                    'coords': hood['centroid'] + candidate['centroid']
                    }