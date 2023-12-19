from enum import Enum
import secrets, os
from datetime import datetime

from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
from dotenv import load_dotenv


### CONSTANTS AND ENVIRONMENT VARIABLES
load_dotenv()
EXAMPLE1 = True
EXAMPLE2 = True


### HELPER CLASSES
class FileFormats(Enum):
    FILE_GEODATABASE = ("File Geodatabase", ".zip") # actually .gdb but the download will be a zip
    GEOJSON = ("GeoJson", ".geojson")
    SHAPEFILE = ("Shapefile", ".zip") # actually .shp+others but the download will be a zip

    def __init__(self, file_name, extension):
        self.file_name = file_name
        self.extension = extension


### FUNCTIONS
def authenticate():
    user = os.environ['AGOL_USERNAME']
    pw = os.environ['AGOL_PASSWORD']
    url = os.environ['AGOL_ORGANISATION_URL']
    gis = GIS(username=user, password=pw, url=url)
    return(gis)

def overwrite_featurelayer_collection(item_id:str, new_file_path:str, gis_portal: GIS = None) -> bool:
    """
    Overwrite a feature layer with a new file, the file must be of the same format as the original file
    Arguments:
        item_id {str} -- the id of the item to overwrite
        new_file_path {str} -- the path to the new file
    Keyword Arguments:
        gis_portal {GIS} -- the gis portal to connect to (default: {None})
    Returns:
        bool -- True if successful, False otherwise

    Notes:
        1. It will overwrite the attribute table (old fields will be deleted, new fields will be added)
        2. it will overwrite the geometry data
    """
    if(gis_portal == None):
        gis_portal = authenticate()

    try:
        item = gis_portal.content.get(item_id)
        feature_layer_collection = FeatureLayerCollection.fromitem(item)
        result = feature_layer_collection.manager.overwrite(new_file_path)
        return result['success']
    except Exception as e:
        print(e) #str(e) == 'Job failed.'
        return False
    

def download_feature_layer_collection_from_agol(item_id:str,
                                                outpath:str,
                                                export_format: FileFormats = FileFormats.FILE_GEODATABASE,
                                                gis_portal: GIS = None) -> str|bool:
    """
    Download a feature layer collection from ArcGIS Online as a filegeodatabase
    Arguments:
        item_id {str} -- the id of the item to download
        outpath {str} -- the path to the output file WITHOUT FILE EXTENSION
    Keyword Arguments:
        gis_portal {GIS} -- the gis portal to connect to (default: {None})
    Returns:
        str|bool -- The path of the downloaded file as string if successful, False otherwise
    """
    if(gis_portal == None):
        gis_portal = authenticate()
    try:
            
        item = gis_portal.content.get(item_id)
        export_title = item.title
        random_title = secrets.token_hex(16) + '_python_temp'
        temp_export_result_item = item.export(random_title, export_format.file_name, parameters=None, wait=True)
        export_file_name = f'{datetime.now().strftime("%Y-%m-%d")}_{export_title}{export_format.extension}'
        downloaded_filepath = temp_export_result_item.download( save_path=outpath, file_name=export_file_name)
        delete_response = temp_export_result_item.delete()
    
        if(downloaded_filepath and delete_response):
            return downloaded_filepath
        else:
            return False
        
    except Exception as e:
        print(e)
        return False

### MAIN
if __name__ == "__main__":

    # 1) Examle 1: Overwrite a feature layer collection with a new local file
    if(EXAMPLE1):
        new_file_path = './data/AM_waterProtectionArea-DE.gdb.zip'
        item_id="4c669b6afdf046b08f819a24445af80e" 
        overwrite_successful = overwrite_featurelayer_collection(item_id, new_file_path)
        print(f"Done - overwrite_successful: {overwrite_successful}")

    # 2) Example 2: Download a feature layer collection from ArcGIS Online as a filegeodatabase, e.g. to archive a snapshot of the data
    if(EXAMPLE2):    
        item_id="4c669b6afdf046b08f819a24445af80e" 
        download_successful = download_feature_layer_collection_from_agol(item_id, './data/json/', FileFormats.GEOJSON)
        print(f"Done - download_successful: {download_successful}")

        download_successful = download_feature_layer_collection_from_agol(item_id, './data/gdb/', FileFormats.FILE_GEODATABASE)
        print(f"Done - download_successful: {download_successful}")

        download_successful = download_feature_layer_collection_from_agol(item_id, './data/shp/', FileFormats.SHAPEFILE)
        print(f"Done - download_successful: {download_successful}")

