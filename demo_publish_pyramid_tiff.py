# 演示案例：使用GeoServerService发布金字塔切片的TIFF(>=2GB)服务

import os
import shutil
from GeoServerService import GeoServerService

# 初始化服务
url = "http://localhost:8080/geoserver/rest" # geoserver url
username = "admin" # geoserver username
password = "geoserver" # geoserver password

service = GeoServerService(url, username, password)

# 准备参数
workspaceName = "test" # geoserver 工作空间名称
layerName = "pyramid_tiff_layer" # geoserver 图层名称
tiffPath = "" # 用于发布的TIFF文件路径
tiffDir = "" # 切片后生成的TIFF金字塔文件夹路径
levels = 4 # 金字塔层级
blockWidth = 2048 # 金字塔每个块的宽度
blockHeight = 2048 # 金字塔每个块的高度

# 检查待生成的文件夹是否存在，如果存在则清空，否则创建
if os.path.isdir(tiffDir):
    shutil.rmtree(tiffDir) 
os.mkdir(tiffDir)

# 检查图层是否已存在，如果存在，则删除
if service.isStoreExist(workspaceName, layerName):
    service.deleteStore(workspaceName, layerName)

# 发布图层
res = service.createPyramidTiffLayer(workspaceName, layerName, tiffPath, tiffDir, levels, blockWidth, blockHeight)
print(res)