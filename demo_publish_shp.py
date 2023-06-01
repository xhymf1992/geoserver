# 演示案例：使用GeoServerService发布SHP服务

from GeoServerService import GeoServerService

# 初始化服务
url = "http://localhost:8080/geoserver/rest" # geoserver url
username = "admin" # geoserver username
password = "geoserver" # geoserver password

service = GeoServerService(url, username, password)

# 准备参数
workspaceName = "test" # geoserver 工作空间名称
layerName = "shp_layer" # geoserver 图层名称
shapePath = "" # 用于发布的shp文件路径，精确到文件，不带后缀
charset = "utf-8" # dbf文件的编码格式，不影响发布，主要影响发布后的属性拾取，如果编码格式不对，拾取到的中文属性会乱码

# 检查工作空间是否存在，如果不存在，则创建
if not service.isWorkspaceExist(workspaceName):
    service.createWorkspace(workspaceName)

# 检查图层是否已存在，如果存在，则删除
if service.isStoreExist(workspaceName, layerName):
    service.deleteStore(workspaceName, layerName)

# 发布图层  
res = service.createShapeLayer(workspaceName, layerName, shapePath, charset)
print(res)