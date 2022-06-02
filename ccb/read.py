"""A series of functions for reading different data formats into memory
"""
import os as _os
import pickle as _pickle

from osgeo import gdal as _gdal

_gdal.UseExceptions()


def is_raster(path):
    """
    Tests if a file is a raster (i.e., gdal readable)
    :param path: the path to the file to check
    :return: bool
    """
    # its a dang raster if GDAL can open it
    try:
        _gdal.Open(path)
        return True
    except RuntimeError:
        return False


def is_csv(path):
    """
    Tests if a file is a CSV (i.e., pandas readable)
    :param path: the path to the file to check
    :return: bool
    """
    # check file ending
    ext = _os.path.splitext(path)[1]
    if ext.lower() in [".csv", ".tsv"]:
        return True
    else:
        return False


def pck(path):
    """
    Reads a python/pickle format data file
    :param path: the path to the input pickle file
    :return: the object stored in the pickle file
    """
    with open(path, "r") as f:
        return _pickle.load(f)


class raster(object):
    def __init__(self, input_file):
        """
        Reads metadata from a raster file and stores it in an object
        :param input_file: a path to a raster file to read
        :return object: An object with raster properties and derivative functions
        """

        # read the gdal reference as read-only
        ref = _gdal.Open(input_file, 0)
        self.file_name = input_file

        # get file dimensions
        self.nx = ref.RasterXSize
        self.ny = ref.RasterYSize
        self.nb = ref.RasterCount

        # get georeferencing info
        self.prj = ref.GetProjection()
        geo = ref.GetGeoTransform()
        self.xmin = geo[0]
        self.xps = geo[1]
        self.xoff = geo[2]
        self.ymax = geo[3]
        self.yoff = geo[4]
        self.yps = geo[5]
        self.xmax = self.xmin + self.xoff + (self.nx * self.xps)
        self.ymin = self.ymax + self.yoff + (self.ny * self.yps)

        # get no-data info
        band = ref.GetRasterBand(1)
        self.no_data = band.GetNoDataValue()

        # get data type
        self.dt = band.DataType

        # create an empty 'data' variable to read into later
        self.data = None

        # get driver info
        self.driver_name = ref.GetDriver().ShortName

        # kill the gdal references
        ref = None
        band = None

    # a function to read raster data from a single band
    def read_band(self, band):
        """
        Reads the raster data from a user-specified band into the self.data variable
        :param band: the 1-based index for the band to read
        :return: updates object.data with a numpy array of raster values
        """
        ref = _gdal.Open(self.file_name, 0)
        band = ref.GetRasterBand(band)
        self.data = band.ReadAsArray()

    # a function to read raster data from all bands
    def read_all(self):
        """
        Reads all bands of raster data
        :return: updates object.data with a numpy array of raster values
        """
        ref = _gdal.Open(self.file_name, 0)
        self.data = ref.ReadAsArray()

    # a function to write raster data to a single band
    def write_band(self, band, data):
        """
        Writes new raster data to a user-specified band
        :param band: a 1-based integer with the band to write to
        :param data: a numpy array with raster data to write
        :return:
        """
        ref = _gdal.Open(self.file_name, 1)
        band = ref.GetRasterBand(band)
        band.WriteArray(data)

        # clean up
        band.FlushCache()
        ref.FlushCache()
        band = None
        ref = None

    # a function to write raster data to all bands
    def write_all(self, data=None):
        """
        Writes new raster data to all bands
        :param data: a numpy array with raster data to write. if not set, writes self.data
        :return:
        """
        ref = _gdal.Open(self.file_name, 1)

        # see which data to write
        if data:
            ref.WriteRaster(data)
        else:
            ref.WriteRaster(self.data)

        # clean up
        ref.FlushCache()
        ref = None

    def write_metadata(self, ref=None):
        """Updates the metadata of a file if changed by the user
        :param ref: the gdal file reference object (a la ref = gdal.Open('some_file.tif', 1)
        :return:
        """
        if ref is None:
            ref = _gdal.Open(self.file_name, 1)

        # update projection and geotransform at file-level
        ref.SetProjection(self.prj)
        ref.SetGeoTransform([self.xmin, self.xps, self.xoff, self.ymax, self.yoff, self.yps])

        # update no-data value band by band
        if self.no_data is not None:
            for band in range(1, self.nb + 1):
                b = ref.GetRasterBand(band)
                b.SetNoDataValue(self.no_data)
                b.FlushCache()
                b = None

        # clean up
        ref.FlushCache()
        ref = None

    def copy(self, file_name, nb=None, driver=None, dt=None, options=None):
        """
        Creates a new raster file and object with a copy of the raster metadata that can be used to write a new derived data product.
        :param file_name: the file path to create as a new reference
        :param nb: the number of bands for the new file
        :param driver: the name of the driver to use. default is the driver of the input reference
        :param dt: the output data type
        :param options: gdal raster creation options, passed as a list
        :return raster: a new raster object with updated metadata. write a new gdal file to disk with those properties written to its header. no raster data is written to this file, only metadata.
        """
        import copy as cp

        # create a copy of the input object to manipulate
        new_obj = cp.copy(self)

        # update with the new parameters
        new_obj.file_name = file_name

        if nb:
            new_obj.nb = nb

        if driver:
            new_obj.driver_name = driver

        if dt:
            new_obj.dt = dt

        # create a new raster file with these parameters, but don't write any data
        ref = _gdal.GetDriverByName(new_obj.driver_name).Create(
            new_obj.file_name, new_obj.nx, new_obj.ny, new_obj.nb, new_obj.dt, options=options
        )

        # set the projection and geotransform parameters
        new_obj.write_metadata(ref=ref)

        # kill the reference and return the new object
        ref = None

        return new_obj
