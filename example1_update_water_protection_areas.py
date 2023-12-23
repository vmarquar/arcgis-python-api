# conda activate gis_env

### IMPORTS
import requests, zipfile, io, re, datetime, os, shutil, tempfile
import xml.etree.ElementTree as ET
from arcgis.gis import GIS
from dotenv import load_dotenv, set_key, find_dotenv

from simple_arcgis_online_functions import overwrite_featurelayer_collection

### CONSTANTS

### FUNCTIONS
def authenticate():
    user = os.environ['AGOL_USERNAME']
    pw = os.environ['AGOL_PASSWORD']
    url = os.environ['AGOL_ORGANISATION_URL']
    gis = GIS(username=user, password=pw, url=url)
    return(gis)

def __download_water_protection_areas(extract_path: str = "/arcgis/home/data/AwF5_EBV") -> list[str]:
    """Download the water protection areas and extract them to the extract_path
    
    Keyword Arguments:
        extract_path {str} -- a drive path to extract the data to (default: {"/arcgis/home/data/AwF5_EBV"})
        
    Returns:
        list[str] -- a list of filenames of the extracted files
    """
    download_url = 'https://geoportal.bafg.de/inspire/download/AM/waterProtectionArea/AM_waterProtectionArea-DE_GDB.zip'
    r = requests.get(download_url)
    with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
        file_list = zip_ref.namelist()
        zip_ref.extractall(extract_path)
    
    # append extract_path to all file names
    file_list = [os.path.join(extract_path, file_name) for file_name in file_list]
    return  file_list

def download_and_extract_xml(metadata_url: str ='https://geoportal.bafg.de/inspire/download/AM/waterProtectionArea/datasetfeed.xml') -> list[dict]:
    response = requests.get(metadata_url)
    xml_data = response.text

    root = ET.fromstring(xml_data)
    namespace = {'atom': '{http://www.w3.org/2005/Atom}'}
    entries = []
    for element in root:
        element.tag.replace(namespace['atom'], '')
        if(element.tag.replace(namespace['atom'], '') == 'entry'):
            data_dict_entry = {child.tag.replace(namespace['atom'], ''): child.text for child in element}

            #if the value matches this timestamp format: '2023-10-06T08:00:00+01:00', convert it to a datetime object use regex to match that format
            if(re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', data_dict_entry['updated'])):
                data_dict_entry['updated'] = datetime.datetime.strptime(data_dict_entry['updated'][:-6], '%Y-%m-%dT%H:%M:%S') # neglect the timezone for now
            entries.append(data_dict_entry)
    return entries

def download_zip_file_from_url(url:str) -> str:
    """
    Download a zip file from an url and return the path to the downloaded file
    the created temp directory will NOT deleted after the function call
    """
    # URL of the file to download
    file_name = url.split('/')[-1]
    file_name = file_name if(file_name[-4:] == '.zip') else 'file.zip'
    r = requests.get(url, stream=True)
    r.raise_for_status()

    # Create a temporary file in the directory
    temp_dir = tempfile.mkdtemp()
    with open(f'{temp_dir}/{file_name}', 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    # The downloaded file is now in temp_dir/file.zip
    print(f'Downloaded file to {temp_dir}/{file_name}')
    return f'{temp_dir}/{file_name}'

def main_check_and_update_waterprotection_areas(item_id:str = '4c669b6afdf046b08f819a24445af80e') -> dict[str, bool]:
    """
    Check if new data is available and update the water protection areas if necessary
    Returns:
        dict[str, bool] -- a dictionary with the keys 'success' and 'overwrite_successful'
    """
    try:
        # 1) load environment and last dates
        load_dotenv()
        water_protection_last_publish_date = datetime.datetime.fromisoformat(os.getenv('WATER_PROTECTION_LAST_PUBLISH_DATE')) if os.getenv('WATER_PROTECTION_LAST_PUBLISH_DATE') else None

        # 2) Get the current publish date
        water_protection_metadata_url = 'https://geoportal.bafg.de/inspire/download/AM/waterProtectionArea/datasetfeed.xml'
        data_entries = download_and_extract_xml(water_protection_metadata_url)
        water_protection_current_publish_date = data_entries[0]['updated']
        
        # 3) Compare the dates
        if((water_protection_last_publish_date == None) or (water_protection_current_publish_date >= water_protection_last_publish_date)):
            # 4) Download the water protection areas to a temp dir
            #    it will be automatically deleted after upload
            downloaded_zip = download_zip_file_from_url('https://geoportal.bafg.de/inspire/download/AM/waterProtectionArea/AM_waterProtectionArea-DE_GDB.zip')
            gis = authenticate()
            overwrite_successful = overwrite_featurelayer_collection(item_id, downloaded_zip)
            print(f"Done - overwrite_successful: {overwrite_successful}")
            # 6) Update the last_updated variable and delete temp files/directory
            os.environ["WATER_PROTECTION_LAST_PUBLISH_DATE"] = water_protection_current_publish_date.isoformat()
            set_key(find_dotenv(), "WATER_PROTECTION_LAST_PUBLISH_DATE", os.environ["WATER_PROTECTION_LAST_PUBLISH_DATE"])
            shutil.rmtree(os.path.dirname(downloaded_zip))
            return {'success': True, 'overwrite_successful': overwrite_successful}
        
        else:
            return {'success': True, 'overwrite_successful': False}
        
    except Exception as e:
        print(e)
        return {'success': False, 'overwrite_successful': False, 'exception': str(e)}

### MAIN
if __name__ == "__main__":
    status = main_check_and_update_waterprotection_areas()
    print(status)
