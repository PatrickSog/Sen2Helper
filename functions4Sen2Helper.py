"""S2GridMaker downloads the orbit kml from ESA and transforms it to a geo-data-frame"""


# noinspection SpellCheckingInspection
#def S2GridMaker():
#    #import wget
#    # import fiona
#    import geopandas as gpd
#    url = 'https://sentinel.esa.int/documents/247904/1955685' \
#          '/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml '
#    s2grid = wget.download(url)
#    # gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
#    s2df = gpd.read_file(s2grid, driver="KML")
#    return s2df

import geopandas as gpd

"""Reads and re-projects given ROI to EPSG:4326"""


# noinspection SpellCheckingInspection
def ReprojectGivenROI(roi):
    roidf = gpd.read_file(roi)  # The driver should not be hard-coded as KML
    roidf = roidf.to_crs({'init': 'epsg:4326'})
    return roidf


"""Reads and re-projects given ROI to EPSG:4326"""


def Sen2ROIIntersects(s2df, roidf):
    wrs_intersection = s2df[s2df.intersects(roidf.geometry[0])]
    tile_list = wrs_intersection["Name"]
    return tile_list  # This should be printed in QGIS from wrs_intersection["Name"]


"""Login for Copernicus Scihub"""


def EnterUsrData(usr_input, pw_input):
    from sentinelsat import SentinelAPI
    usr = usr_input  # This shall be done via the GUI in Username
    pw = pw_input  # This shall be done via the GUI in Password
    api = SentinelAPI(usr, pw)
    return api


"""Function for specifying investigation"""


# noinspection SpellCheckingInspection
def EnterInv(tmininput, tmaxinput, level_string):
    pf = "Sentinel-2"  # This should not be hard-coded in the future
    pt = level_string  # "S2MSI1C"  # This should not be hard-coded in the future
    tmin = tmininput  # This shall be done via the GUI in StartDate
    tmax = tmaxinput  # This shall be done via the GUI in EndDate
    query_kwargs = {'platformname': pf,
                    'producttype': pt,
                    'date': (tmin, tmax)}
    return query_kwargs


"""Sentinel-2 Level-1C Downloader"""


# noinspection SpellCheckingInspection
def S2L1CDL(tilelist, query_kwargs, api, s2path):
    from collections import OrderedDict
    products = OrderedDict()
    for tile in tilelist:
        kw = query_kwargs.copy()
        kw['tileid'] = tile
        pp = api.query(**kw)
        products.update(pp)
    api.download_all(products, directory_path=s2path)


"""Sentinel-2 Level-1C to Level-2A processing"""


def L2ABatchProcess(s2c_dir, s2path):
    import zipfile
    import os
    import subprocess
    from tqdm import tqdm
    s2list = os.listdir(s2path)
    for file in tqdm(s2list):
        if file.endswith(".zip"):
            raster = s2path + "/" + file
            with zipfile.ZipFile(raster, 'r') as zipObj:
                zipObj.extractall(path=s2path)
            x_raster = raster.split(".")[0]
            x_raster = x_raster + ".SAFE"
            #os.chdir(os.path.abspath(s2c_dir))
            process = subprocess.Popen([s2c_dir + "/bin/" + "L2A_Process", x_raster])
            process.wait()


"""Check OS and install sen2Cor, if it is not installed already"""


def CheckSen2Cor():
    import os
    import platform
    import stat
    import subprocess
    import wget
    import zipfile
    if platform.system() == 'Linux':
        s2c = "http://step.esa.int/thirdparties/sen2cor/2.5.5/Sen2Cor-02.05.05-Linux64.run"
    elif platform.system() == 'Darwin':
        s2c = "http://step.esa.int/thirdparties/sen2cor/2.5.5/Sen2Cor-02.05.05-Darwin64.run"
    elif platform.system() == 'Windows':
        s2c = "http://step.esa.int/thirdparties/sen2cor/2.5.5/Sen2Cor-02.05.05-win64.zip"
    name = s2c.split("/")[-1]
    path = os.path.dirname(os.path.realpath(__file__))

    if platform.system() == 'Windows':
        sen2cor = ".".join(name.split(".")[:-1])
        sen2cor = path + "/" + sen2cor
        if not os.path.isdir(path + "/" + name):
           wget.download(url=s2c,out=path)
           with zipfile.ZipFile(path + "/" + name, 'r') as zipObj:
                zipObj.extractall(path=path)
    else:
        sen2cor = path + "/" + name
        if not os.path.isdir(path + "/" + name):
           wget.download(url=s2c,out=path)
           mode = os.stat(sen2cor).st_mode
           os.chmod(sen2cor,stat.S_IEXEC|mode)
           result = subprocess.Popen([sen2cor], stdout=subprocess.PIPE)
           print(result.communicate())

    sen2cor = ".".join(name.split(".")[:-1])
    return sen2cor

