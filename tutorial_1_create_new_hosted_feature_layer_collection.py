# --- Tutorial 1: Create a new hosted feature layer ---
# --- https://developers.arcgis.com/documentation/mapping-apis-and-services/data-hosting/tutorials/tools/define-a-new-feature-layer/

### IMPORTS
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayerCollection, FeatureLayer

from simple_arcgis_online_functions import authenticate

### CONSTANTS
EXAMPLE1 = False
EXAMPLE2 = False
EXAMPLE3 = True

# service parameters
create_params = {
    "maxRecordCount": 2000,
    "supportedQueryFormats": "JSON",
    "capabilities": "Query,Extract",
    "description": "Place points along the California coast line",
    "allowGeometryUpdates": True,
    "hasStaticData": True,
    "units": "esriMeters",
    "syncEnabled": False,
    "editorTrackingInfo": {
        "enableEditorTracking": False,
        "enableOwnershipAccessControl": False,
        "allowOthersToQuery": True,
        "allowOthersToUpdate": True,
        "allowOthersToDelete": False,
        "allowAnonymousToUpdate": True,
        "allowAnonymousToDelete": False,
    },
    "xssPreventionInfo": {
        "xssPreventionEnabled": True,
        "xssPreventionRule": "InputOnly",
        "xssInputRule": "rejectInvalid",
    },
    "initialExtent": {
        "xmin": -134.74729261792592,
        "ymin": 23.56096242376989,
        "xmax": -55.695547615409396,
        "ymax": 50.309217030288835,
        "spatialReference": {"wkid": 4326},
    },
    "spatialReference": {"wkid": 4326},
    "tables": [],
    "name": "my_points_tutorial",
}

# define layer props
layer_schema = {
    "layers": [
        {
            "name": "my_points",
            "type": "Feature Layer",
            "defaultVisibility": True,
            "relationships": [],
            "isDataVersioned": False,
            "supportsRollbackOnFailureParameter": True,
            "supportsAdvancedQueries": False,
            "geometryType": "esriGeometryPoint",
            "minScale": 0,
            "maxScale": 0,
            "extent": {
                "xmin": -134.74729261792592,
                "ymin": 23.56096242376989,
                "xmax": -55.695547615409396,
                "ymax": 50.309217030288835,
                "spatialReference": {"wkid": 4326},
            },
            "drawingInfo": {
                "transparency": 0,
                "labelingInfo": None,
                "renderer": {
                    "type": "simple",
                    "symbol": {
                        "color": [20, 158, 206, 130],
                        "size": 18,
                        "angle": 0,
                        "xoffset": 0,
                        "yoffset": 0,
                        "type": "esriSMS",
                        "style": "esriSMSCircle",
                        "outline": {
                            "color": [255, 255, 255, 220],
                            "width": 2.25,
                            "type": "esriSLS",
                            "style": "esriSLSSolid",
                        },
                    },
                },
            },
            "allowGeometryUpdates": True,
            "hasAttachments": True,
            "htmlPopupType": "esriServerHTMLPopupTypeNone",
            "hasM": False,
            "hasZ": False,
            "objectIdField": "OBJECTID",
            "fields": [
                {
                    "name": "OBJECTID",
                    "type": "esriFieldTypeOID",
                    "alias": "OBJECTID",
                    "sqlType": "sqlTypeOther",
                    "nullable": False,
                    "editable": False,
                    "domain": None,
                    "defaultValue": None,
                },
                {
                    "name": "id",
                    "type": "esriFieldTypeInteger",
                    "alias": "id",
                    "sqlType": "sqlTypeInteger",
                    "nullable": True,
                    "editable": True,
                    "domain": None,
                    "defaultValue": None,
                },
                {
                    "name": "name",
                    "type": "esriFieldTypeString",
                    "alias": "name",
                    "sqlType": "sqlTypeNVarchar",
                    "nullable": True,
                    "editable": True,
                    "domain": None,
                    "defaultValue": None,
                    "length": 256,
                },
                {
                    "name": "rating",
                    "type": "esriFieldTypeString",
                    "alias": "rating",
                    "sqlType": "sqlTypeNVarchar",
                    "nullable": True,
                    "editable": True,
                    "domain": None,
                    "defaultValue": None,
                    "length": 256,
                },
            ],
            "templates": [
                {
                    "name": "New Feature",
                    "description": "",
                    "drawingTool": "esriFeatureEditToolPoint",
                    "prototype": {
                        "attributes": {
                            "id": None,
                            "name": None,
                            "rating": None,
                        }
                    },
                }
            ],
            "supportedQueryFormats": "JSON",
            "hasStaticData": True,
            "maxRecordCount": 10000,
            "capabilities": "Query,Extract",
        }
    ]
}

def create_new_hosted_feature_layer_collection(title:str, create_params:dict, layer_schema:dict, gis_portal: GIS = None) -> FeatureLayerCollection | bool:
    """
    Create a new hosted feature layer collection
    Arguments:
        title {str} -- the title of the new feature layer collection
        create_params {dict} -- the parameters to create the feature layer collection
        layer_schema {dict} -- the layer schema to create the feature layer collection
    Keyword Arguments:
        gis_portal {GIS} -- the gis portal to connect to (default: {None})
    Returns:
        FeatureLayerCollection -- the created feature layer collection
    """
    if(gis_portal == None):
        gis_portal = authenticate()
    try:
        new_service = gis_portal.content.create_service(
            name=title,
            create_params=create_params,
            tags="Beach Access,Malibu",
        )
        new_feature_layer_coll = FeatureLayerCollection.fromitem(new_service)
        new_feature_layer_coll.manager.add_to_definition(layer_schema)
        return new_feature_layer_coll
    except Exception as e:
        print(e)
        return False
    
def enable_editing_on_feature_layer_collection(gis_portal: GIS, item_id:str) -> bool:
    try:
        item = gis_portal.content.get(item_id)
        feature_layer = FeatureLayerCollection.fromitem(item)
        # update capabilities to enable editing
        results = feature_layer.manager.update_definition(
            {"capabilities": "Query, Extract, Editing, Create, Delete, Update"}
        )
        return(results['success'])
    except Exception as e:
        print(e)
        return False
    
def add_features_to_feature_layer(feature_layer:FeatureLayer):
    zuma_beach = {
        "geometry": {
            "x": 34.01757,
            "y": -118.82549,
            "spatialReference": {"wkid": 4326},
        },
        "attributes": {"id": 1, "name": "Zuma Beach", "rating": "Good"},
    }

    westward_beach = {
        "geometry": {
            "x": 34.01757,
            "y": -118.82549,
            "spatialReference": {"wkid": 4326},
        },
        "attributes": {"id": 2, "name": "Westward Beach", "rating": "Excellent"},
    }
    try:
        results = feature_layer.edit_features(adds=[zuma_beach, westward_beach])
        return(results["addResults"])
    except Exception as e:
        print(e)
        return False

def get_feature_layer(item_id:str=None, layer_name:str=None, layer_url:str=None) -> FeatureLayer | bool:
    """
    Get a feature layer from ArcGIS Online
    Arguments:
        
        item_id {str} -- the id of the FeatureLayerCollection (= container)
        layer_name {str} -- and additionally the name of the layer
        
        or alternatively:

        layer_url {str} -- the explicit url of the layer
    Returns:
        FeatureLayer -- the feature layer
    """
    try: 
        if(layer_url != None and layer_url[-1].isdigit() == True):
            return FeatureLayer(layer_url)
        elif(item_id != None and layer_name != None):
            item = portal.content.get(item_id)
            feature_layer = [lyr for lyr in item.layers if lyr.properties.name == layer_name][0]
            return feature_layer
        else:
            print('Please provide either a) item_id and layer_name or b) a layer_url')
            return False
    except Exception as e:
        print(e)
        print('Please provide either a) item_id and layer_name or b) a layer_url')
        print('The layer url must have a number at the end, e.g. https://services-eu1.arcgis.com/blablabla/arcgis/rest/services/AM_waterProtectionArea_DE_gdb/FeatureServer/0')
        return False


# update attributes and add fields
def modify_fields_of_feature_layer(feature_layer:FeatureLayer, fields:list[dict]=None) -> bool:
    """
    feature_layer.manager.delete_from_definition({'fields':[{"name":"rating"}]})
    update_definition({"fields": fields})
    add_to_definition({"fields": fields})

    "layerAdminOperationsOptions": {
        "deleteFromDefinition": [
            "xssTrustedFields",
            "fields",
            "indexes",
            "relationships"
            ],
        "addToDefiniton": [
            "fields",
            "indexes"
        ],
        "updateDefinition": [
            "name",
            "xssTrustedFields",
            "displayField",
            "description",
            "copyrightText",
            "editFieldsInfo",
            "minScale",
            "maxScale",
            "fields",
            "maxRecordCount",
            "drawingInfo",
            "types",
            "templates",
            "indexes",
            "defaultVisibility",
            "hasAttachments",
            "propagateVisibleFields",
            "hasGeometryProperties",
            "attachmentProperties",
            "lodInfos",
            "typeIdField",
            "timeInfo",
            "allowUpdateWithoutMValues",
            "maxRecordCountFactor",
            "allowGeometryUpdates",
            "capabilities",
            "ownershipBasedAccessControlForFeatures",
            "onlyAllowTrueCurveUpdatesByTrueCurveClients",
            "allowTrueCurvesUpdates"
        ]
    }
    """
    try:
        results = feature_layer.manager.add_to_definition({"fields": fields})
        return(results['success'])
    except Exception as e:
        print(e)
        return False


# write main
if __name__ == "__main__":

    if(EXAMPLE1):
        portal = authenticate()
        new_feature_layer = create_new_hosted_feature_layer_collection('my_points_tutorial', create_params, layer_schema, portal)
        status = enable_editing_on_feature_layer_collection(portal, new_feature_layer.properties['serviceItemId'], new_feature_layer)

    if(EXAMPLE2):
        add_features_to_feature_layer()

    if(EXAMPLE3):
        portal = authenticate()

        fl = get_feature_layer(item_id='577bd8ec6ce24a4aabfcc5fd4aed13fe', layer_name='my_points')
        additional_fields = [{  "name": "comment2",
                                "type": "esriFieldTypeString",
                                "alias": "comment2",
                                "sqlType": "sqlTypeNVarchar",
                                "nullable": True,
                                "editable": True,
                                "domain": None,
                                "defaultValue": None,
                                "length": 256},
                            {"name": "feld_mit_auwahl3",
                                "type": "esriFieldTypeString",
                                "alias": "",
                                "sqlType": "sqlTypeOther",
                                "length": 256,
                                "nullable": True,
                                "editable": True,
                                "visible": True,
                                "domain": {
                                    "type": "codedValue",
                                    "name": "domain-blablabla-my-unique-value-str",
                                    "codedValues": [
                                    {
                                        "name": "label1",
                                        "code": "value1"
                                    },
                                    {
                                        "name": "label2",
                                        "code": "value2"
                                    },
                                    {
                                        "name": "label3",
                                        "code": "value3"
                                    }
                                    ]
                                },
                                "defaultValue": None
                                }   
                            ]
        update_successful = modify_fields_of_feature_layer(fl, fields=additional_fields)
        print(update_successful)