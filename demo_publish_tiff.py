# 演示案例：使用GeoServerService发布普通TIFF(<2GB)服务

from GeoServerService import GeoServerService

# 初始化服务
url = "http://localhost:8080/geoserver/rest" # geoserver url
username = "admin" # geoserver username
password = "geoserver" # geoserver password

service = GeoServerService(url, username, password)

# 准备参数
workspaceName = "test" # geoserver 工作空间名称
layerName = "tiff_layer" # geoserver 图层名称
tiffPath = "" # 用于发布的TIFF文件路径

# 检查工作空间是否存在，如果不存在，则创建
if not service.isWorkspaceExist(workspaceName):
    service.createWorkspace(workspaceName)

# 检查图层是否已存在，如果存在，则删除
if service.isStoreExist(workspaceName, layerName):
    service.deleteStore(workspaceName, layerName)

# 发布图层  
res = service.createTiffLayer(workspaceName, layerName, tiffPath)
print(res)