from pgsync import plugin

class GeoPointPlugin(plugin.Plugin):
    name = 'GeoPoint'

    def transform(self, doc, **kwargs):
        def add_geo_point(obj):
            if not isinstance(obj, dict):
                return

            # Safely check and add 'point' if 'latitude' and 'longitude' are present
            lat = obj.get('latitude')
            lon = obj.get('longitude')
            if lat is not None and lon is not None:
                obj['point'] = {'lat': lat, 'lon': lon}

            # Recurse into nested dicts and lists
            for key in list(obj.keys()):  # Use list() to avoid dict size change issues
                value = obj[key]
                if isinstance(value, dict):
                    add_geo_point(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            add_geo_point(item)

        add_geo_point(doc)
        return doc