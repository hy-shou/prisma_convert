import h5py
from osgeo import gdal, osr, gdalnumeric
from osgeo.gdalconst import *
from pyproj import CRS
import numpy as np
production = 'PRS_L1_HCO'
file_time = '20200515211002'
file_name =  r'F:/data/PRISMA/PRS_L1_STD_OFFL_20200515211002_20200515211007_0001/PRS_L1_STD_OFFL_20200515211002_20200515211007_0001.he5'
# ['PRS_L1_HCO', 'PRS_L1_HRC', 'PRS_L1_PCO', 'PRS_L1_PRC']>

def convert():

    # 1.获取原数据信息
    # 该数据只有地理坐标WGS84
    f = h5py.File(file_name,  'r')
    data = f['HDFEOS']['SWATHS'][production]['Data Fields']['VNIR_Cube']
    Lat = f['HDFEOS']['SWATHS'][production]['Geolocation Fields']['Latitude_VNIR']
    Lon = f['HDFEOS']['SWATHS'][production]['Geolocation Fields']['Longitude_VNIR']
    im_width = data.shape[0]  # 栅格矩阵的列数
    im_height = data.shape[2]  # 栅格矩阵的行数
    im_bands = data.shape[1]
    # ds_array = ds.ReadAsArray(0, 0, im_width, im_height)  # 获取原数据信息，包括数据类型int16，维度，数组等信息

    ds_array = np.transpose(np.array(data),(1, 2, 0))

    # 224，1148行，1185列
    # # 设置数据类型(原图像有负值)
    datatype = gdal.GDT_Float32
    TopRightLongitude = Lon[0,999]
    TopLeftLongitude = Lon[0,0]
    TopLeftLatitude = Lat[0,0]
    BottomLeftLatitude = Lat[999,0]
    ysize = xsize = 1000
    # 2.原图像的仿射变换矩阵参数，即im_geotrans
    Lon_Res = (TopRightLongitude - TopLeftLongitude) / (float(ysize))
    Lat_Res = (TopLeftLatitude - BottomLeftLatitude) / (float(xsize))

    img_transf = (Lon[0,0], Lon_Res, 0.0, Lat[0,0], 0.0, Lat_Res)
    # # 网站查询的WGS84-UTM50N坐标信息https://spatialreference.org/ref/epsg/32650/html/
    img_proj = '''PROJCS["WGS 84 / UTM zone 4N",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-159],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","32604"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]'''

    # 3.设置新文件及各项参数
    filename = './PRS_VNIR' + file_time + '_'+ production + '.tif'
    driver = gdal.GetDriverByName("GTiff")  # 创建文件驱动


    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)
    # dataset.SetGeoTransform(左上角x坐标,东西方向上图像的分辨率,地图的旋转角度,左上角y坐标,地图的旋转角度,南北方向上地图的分辨率)
    dataset.SetGeoTransform(img_transf)  # 写入仿射变换参数
    dataset.SetProjection(img_proj)  # 写入投影

    out_band = dataset.GetRasterBand(im_bands)
    # 写入影像数据
    for i in range(ds_array.shape[0]):
        dataset.GetRasterBand(i+1).WriteArray(np.flip(ds_array[65-i],axis=1))

    del dataset

if __name__ == '__main__':
    convert()
