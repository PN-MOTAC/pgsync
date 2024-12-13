from pgsync import plugin

class GeoPointPlugin(plugin.Plugin):
    name = 'GeoPoint'

    def transform(self, doc, **kwargs):
        # Extract latitude and longitude from the document
        latitude = doc.get('latitude')
        longitude = doc.get('longitude')

        # Add a geo_point field if both lat and lon exist
        if latitude is not None and longitude is not None:
            doc['point'] = {'lat': latitude, 'lon': longitude}

        # Return the transformed document
        return doc