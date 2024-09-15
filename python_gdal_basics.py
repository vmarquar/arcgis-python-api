def create_example_gdb_from_gdal():
    """
    This Method needs a valid gdal installation. On macos use `brew install gdal` and `poetry run pip install gdal`. 
    """
    from osgeo import ogr, osr

    # Register the GDAL drivers
    ogr.RegisterAll()

    # Open the File Geodatabase using the OpenFileGDB driver
    driver = ogr.GetDriverByName("OpenFileGDB")
    output_file = "./test.gdb"

    # Create a new shapefile or other vector data source
    # driver = ogr.GetDriverByName("ESRI Shapefile")  # Use "GPKG" for GeoPackage
    # output_file = "fake_data.shp"  # For GeoPackage, use: "fake_data.gpkg"

    # Remove the output file if it already exists
    if driver.DeleteDataSource(output_file):
        print(f"Removed existing file: {output_file}")

    # Create the data source (shapefile or other)
    data_source = driver.CreateDataSource(output_file)

    # Create a spatial reference (WGS84 in this case)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # EPSG:4326 = WGS84 (latitude/longitude)

    # Create a layer (point geometry in this case)
    layer = data_source.CreateLayer("FakePoints", srs, ogr.wkbPoint)

    # Define the attributes (fields)
    field_name = ogr.FieldDefn("Name", ogr.OFTString)  # String field
    field_name.SetWidth(24)  # Max length for the string

    field_value = ogr.FieldDefn("Value", ogr.OFTReal)  # Numeric field

    # Add the fields to the layer
    layer.CreateField(field_name)
    layer.CreateField(field_value)

    # Create some fake point features
    fake_data = [
        ("Point1", 100.5, 34.05, -118.25),
        ("Point2", 200.0, 36.16, -115.15),
        ("Point3", 300.1, 40.71, -74.00),
    ]

    # Loop through the fake data and create a feature for each
    for name, value, lat, lon in fake_data:
        # Create a new feature
        feature = ogr.Feature(layer.GetLayerDefn())
        
        # Set the attribute values
        feature.SetField("Name", name)
        feature.SetField("Value", value)
        
        # Create the point geometry
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)  # OGR uses (lon, lat) = (x, y)
        
        # Set the feature's geometry
        feature.SetGeometry(point)
        
        # Add the feature to the layer
        layer.CreateFeature(feature)
        
        # Destroy the feature to free memory
        feature = None

    # Close the data source to save the file
    data_source = None
    return(output_file)

def create_zip_file(filepath):
    import shutil
    import os

    # Compress the .gdb folder into a .zip file
    shutil.make_archive(os.path.splitext(filepath)[0], 'zip', filepath)
    return(os.path.splitext(filepath)[0]+'.zip')


def create_feature_service_from_gdb(gdb_zip):
    from dotenv import load_dotenv
    from arcgis import GIS
    import os

    load_dotenv(".env")
    gis = GIS(os.getenv("AGOL_ORGANISATION_URL"), os.getenv("AGOL_USERNAME"), os.getenv("AGOL_PASSWORD"))

    gdb_item = gis.content.add({
    'title': 'Test GDB Upload',
    'type': 'File Geodatabase'
    }, data=gdb_zip)

    print(f"Uploaded GDB as item: {gdb_item.id}")

    # Step 4: Publish the item as a feature layer
    feature_layer_item = gdb_item.publish()



if __name__ == "__main__":

    # 1) Create an example File Geodatabase with 3 Points in it
    filepath = create_example_gdb_from_gdal()

    # 2) create zip file
    zip_path = create_zip_file(filepath)

    # 3) upload to AGOL
    create_feature_service_from_gdb(zip_path)

