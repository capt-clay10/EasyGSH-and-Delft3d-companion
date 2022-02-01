from processing.core.Processing import Processing
import processing
import sys
from qgis.core import (
    QgsApplication,
    QgsProcessingFeedback,
    QgsVectorLayer
)

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
QgsApplication.setPrefixPath(r'C:\OSGeo4W\apps\qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Append the path where processing plugin can be found
sys.path.append(r'C:\OSGeo4W\apps\qgis-ltr\python\plugins')


Processing.initialize()


def create_grd_lines(grid_points, crs, order_field, group_field, out_path):
    """Take """
    path_grd_points_qgs = grid_points.replace('\\', '/')

    points_to_path_params = {'INPUT': f'delimitedtext://file:///{path_grd_points_qgs}?'
                             f'type=csv&maxFields=10000&detectTypes=yes&xField=x&yField=y&'
                             f'crs=EPSG:{crs}&spatialIndex=no&subsetIndex=no&watchFile=no',
                             'CLOSE_PATH': False,
                             'ORDER_FIELD': order_field,
                             'GROUP_FIELD': group_field,
                             'DATE_FORMAT': '',
                             'OUTPUT': 'TEMPORARY_OUTPUT'}
    points_to_path_results = processing.run("qgis:pointstopath", points_to_path_params)

    layer_name = f'grd_{group_field}_lines'  # set layer name according to GROUP_FIELD

    save_features_params = {'INPUT': points_to_path_results['OUTPUT'],
                            'OUTPUT': out_path,
                            'LAYER_NAME': layer_name
                            }
    processing.run("native:savefeatures", save_features_params)
