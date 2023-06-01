import subprocess
import geoserver.util
from GeoServerCatalog import GeoServerCatalog


class GeoServerService(object):
    """
    基于GeoServerCatalog库封装的常用服务类
    """
    def __init__(self, url, username, password) -> None:
        self.__cat = GeoServerCatalog(url, username, password)

    def save(self, obj):
        self.__cat.save(obj)

    def getWorkspace(self, workspaceName):
        """
        通过名称获取工作空间
        workspaceName： 工作空间的名称
        return Workspace
        """

        return self.__cat.get_workspace(workspaceName)

    def isWorkspaceExist(self, workspaceName):
        """
        判断工作空间是否存在
        workspaceName： 工作空间的名称
        return True-存在;False-不存在
        """

        res = self.getWorkspace(workspaceName)
        if res == None:
            return False
        else:
            return True

    def createWorkspace(self, workspaceName):
        """
        创建工作空间
        workspaceName： 工作空间的名称
        return {
            status: 状态，success-创建成功;fail-创建失败
            info: 信息, success-""; fail-工作空间已存在；其他信息
            data: None
        }
        """

        res = {
            "status": "fail",
            "info": "",
            "data": None
        }

        try:
            if self.isWorkspaceExist(workspaceName):
                res["info"] = "工作空间已存在：{0}".format(workspaceName)
                return res

            self.__cat.create_workspace(workspaceName, "http://{0}.com".format(workspaceName))
            res["status"] = "success"
            return res
        except Exception as e:
            res["info"] = repr(e)
            return res

    def deleteWorkspace(self, workspaceName):
        """
        删除工作空间（会删除工作空间下的所有内容，包括图层和样式）
        workspaceName： 工作空间的名称
        """

        workspace = self.getWorkspace(workspaceName)
        if workspace != None:
            self.__cat.delete(workspace, None, True)

    def getStore(self, workspaceName, storeName):
        """
        通过名称获取数据存储
        workspaceName： 数据存储所在的工作空间的名称
        storeName：数据存储的名称
        return Store
        """

        return self.__cat.get_store(storeName, workspaceName)
    
    def isStoreExist(self, workspaceName, storeName):
        """
        判断数据存储是否存在
        workspaceName： 数据存储所在的工作空间的名称
        storeName：数据存储的名称
        return True-存在;False-不存在
        """

        res = self.getStore(workspaceName, storeName)
        if res == None:
            return False
        else:
            return True
    
    def deleteStore(self, workspaceName, storeName):
        """
        删除数据存储
        workspaceName： 数据存储所在的工作空间的名称
        storeName：数据存储的名称
        """

        store = self.getStore(workspaceName, storeName)
        if store != None:
            self.__cat.delete(store, None, True)

    def getLayer(self, workspaceName, layerName):
        """
        通过名称获取图层
        workspaceName： 图层所在的工作空间的名称
        layerName：图层的名称
        return Layer
        """

        layerNameReg = "{0}:{1}".format(workspaceName, layerName)
        return self.__cat.get_layer(layerNameReg)

    def isLayerExist(self, workspaceName, layerName):
        """
        判断图层是否存在
        workspaceName： 图层所在的工作空间的名称
        layerName：图层的名称
        return True-存在;False-不存在
        """

        res = self.getLayer(workspaceName, layerName)
        if res == None:
            return False
        else:
            return True

    def createShapeLayer(self, workspaceName, layerName, shapePath, charset):
        """
        创建Shp图层
        workspaceName： 图层所在的工作空间的名称
        layerName：图层的名称
        shapePath：shape文件的路径
        charset：dbf的字符集
        styleParas：图层的样式参数, 
                   point-{type:circle/rectangle/star, color:"#000000", transparency:0.5, size:10}
                   polyline/line-{color:"#000000", width:1}
                   polygon-{fill_color:"#AAAAAA", outline_color:"#000000", outline_width:1}
        return {
            status: 状态，success-创建成功;fail-创建失败
            info: 信息, success-""; fail-工作空间不存在/图层已存在/其他信息
            data: Layer
        }
        """

        res = {
            "status": "fail",
            "info": "",
            "data": None
        }

        try:
            # 判断工作空间是否存在
            if not self.isWorkspaceExist(workspaceName):
                res["info"] = "工作空间不存在：{0}".format(workspaceName)
                return res

            # 判断图层是否存在
            if self.isLayerExist(workspaceName, layerName):
                res["info"] = "图层已存在：{0}".format(layerName)
                return res

            # 创建图层
            workspace = self.getWorkspace(workspaceName)
            try:
                data = geoserver.util.shapefile_and_friends(shapePath)
                self.__cat.create_featurestore(layerName, data, workspace, True, charset)
            except Exception as e:
                res["info"] = "文件解析错误"
                return res

            # 获取创建的图层
            layer = self.getLayer(workspaceName, layerName)
            styleType = layer.default_style.name
            
            res["status"] = "success"
            res["data"] = {
                "layer": layer,
                "default_style": styleType
            }
            return res
        except Exception as e:
            res["info"] = repr(e)
            return res

    def __createTiffLayer(self, workspaceName, layerName, tiffPath, pyramid=False):
        """
        创建Tiff图层
        workspaceName： 图层所在的工作空间的名称
        layerName：图层的名称
        tiffPath：tiff文件/夹的路径
        pyramid: 是否为金字塔结构,默认false
        return {
            status: 状态，success-创建成功;fail-创建失败
            info: 信息, success-""; fail-工作空间不存在/图层已存在/其他信息
            data: {
                layer：生成的图层对象,
                default_style: 图层的默认样式
            }
        }
        """

        res = {
            "status": "fail",
            "info": "",
            "data": None
        }

        try:
            # 判断工作空间是否存在
            if not self.isWorkspaceExist(workspaceName):
                res["info"] = "工作空间不存在：{0}".format(workspaceName)
                return res

            # 判断图层是否存在
            if self.isLayerExist(workspaceName, layerName):
                res["info"] = "图层已存在：{0}".format(layerName)
                return res

            # 创建图层
            workspace = self.getWorkspace(workspaceName)
            try:
                tiffType = "GeoTIFF"
                if pyramid:
                    tiffType = "ImagePyramid"

                self.__cat.create_coveragestore(name=layerName, workspace=workspace, path=tiffPath, type=tiffType, layer_name=layerName)
            except Exception as e:
                res["info"] = "文件解析错误"
                return res

            # 获取创建的图层
            layer = self.getLayer(workspaceName, layerName)
            styleType = layer.default_style.name
            
            res["status"] = "success"
            res["data"] = {
                "layer": layer,
                "default_style": styleType
            }
            return res
        except Exception as e:
            res["info"] = repr(e)
            return res

    def createTiffLayer(self, workspaceName, layerName, tiffPath):
        """
        创建Tiff图层：适用于文件大小<2GB的Tiff
        workspaceName： 图层所在的工作空间的名称
        layerName：图层的名称
        tiffPath：tiff文件的路径
        return {
            status: 状态，success-创建成功;fail-创建失败
            info: 信息, success-""; fail-工作空间不存在/图层已存在/其他信息
            data: Layer
        }
        """

        return self.__createTiffLayer(workspaceName, layerName, tiffPath)

    def createPyramidTiff(self, tiffPath, tiffDir, levels=4, blockWidth=2048, blockHeight=2048):
        """
        对tiff进行金字塔切片
        tiffPath：tiff文件的路径
        tiffDir：生成的金字塔文件夹的路径
        level：金字塔层级，可选，默认为4
        blockWidth: 金字塔切块的宽度分辨率，可选，默认为2048
        blockHeight: 金字塔切块的高度分辨率，可选，默认为2048
        """
        exeStr = 'python gdal_retile.py -v -r bilinear -ot BYTE -levels {0} -ps {1} {2} -co "ALPHA=YES" -targetDir {3} {4}'.format(levels, blockWidth, blockHeight, tiffDir, tiffPath)
        process = subprocess.Popen(exeStr, shell=True)
        process.wait()

    def createPyramidTiffLayer(self, workspaceName, layerName, tiffPath, tiffDir, levels=4, blockWidth=2048, blockHeight=2048):
        """
        创建金字塔切片后的Tiff图层：适用于文件大小>=2GB的Tiff
        workspaceName： 图层所在的工作空间的名称
        layerName：图层的名称
        tiffPath：tiff文件的路径
        tiffDir：生成的金字塔文件夹的路径
        level：金字塔层级，可选，默认为4
        blockWidth: 金字塔切块的宽度分辨率，可选，默认为2048
        blockHeight: 金字塔切块的高度分辨率，可选，默认为2048
        return {
            status: 状态，success-创建成功;fail-创建失败
            info: 信息, success-""; fail-工作空间不存在/图层已存在/其他信息
            data: {
                layer：生成的图层对象,
                default_style: 图层的默认样式
            }
        }
        """
        res = {
            "status": "fail",
            "info": "",
            "data": None
        }
        try:
            # 先对tiff进行切片，生成金字塔结构目录
            try:
                self.createPyramidTiff(tiffPath, tiffDir, levels, blockWidth, blockHeight)
            except Exception as e:
                res["info"] = "切片错误"
                return res

            # 再创建金字塔数据图层
            return self.__createTiffLayer(workspaceName, layerName, tiffDir, True)
        except Exception as e:
            res["info"] = repr(e)
            return res

    def deleteLayer(self, workspaceName, layerName):
        """
        删除图层
        workspaceName： 图层所在的工作空间的名称
        layerName：图层的名称
        """

        layer = self.getLayer(workspaceName, layerName)
        if layer != None:
            self.__cat.delete(layer, None, True)

    def __getPointStyle(self, styleParas):
        """
        生成点类型的样式xml
        styleParas：样式参数 {type:circle/rectangle/star, color:"#000000", transparency:0.5, size:10}
        return xml
        """
        
        type = "circle"
        if "type" in styleParas:
            type = styleParas["type"]

        color = "#000000"
        if "color" in styleParas:
            color = styleParas["color"]

        transparency = 0
        if "transparency" in styleParas:
            transparency = styleParas["transparency"]

        size = 1
        if "size" in styleParas:
            size = styleParas["size"]

        style = '<?xml version="1.0" encoding="UTF-8"?>\r\n \
            <StyledLayerDescriptor version="1.0.0" \r\n \
                xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" \r\n \
                xmlns="http://www.opengis.net/sld" \r\n \
                xmlns:ogc="http://www.opengis.net/ogc" \r\n \
                xmlns:xlink="http://www.w3.org/1999/xlink" \r\n \
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n \
                <NamedLayer>\r\n \
                    <Name>default_point</Name>\r\n \
                    <UserStyle>\r\n \
                        <FeatureTypeStyle>\r\n \
                            <Rule>\r\n \
                                <PointSymbolizer>\r\n \
                                    <Graphic>\r\n \
                                        <Mark>\r\n \
                                            <WellKnownName>{0}</WellKnownName>\r\n \
                                            <Fill>\r\n \
                                              <CssParameter name="fill">{1}</CssParameter>\r\n \
                                              <CssParameter name="fill-opacity">{2}</CssParameter>\r\n \
                                            </Fill>\r\n \
                                        </Mark>\r\n \
                                        <Size>{3}</Size>\r\n \
                                    </Graphic>\r\n \
                                </PointSymbolizer>\r\n \
                            </Rule>\r\n \
                        </FeatureTypeStyle>\r\n \
                    </UserStyle>\r\n \
                </NamedLayer>\r\n\
            </StyledLayerDescriptor>'.format(type, color, 1.0-transparency, size)
        return style
    
    def __getPolylineStyle(self, styleParas):
        """
        生成线类型的样式xml
        styleParas：样式参数 {color:"#000000", width:1}
        return xml
        """

        color = "#000000"
        if "color" in styleParas:
            color = styleParas["color"]

        width = 1
        if "width" in styleParas:
            width = styleParas["width"]

        style = '<?xml version="1.0" encoding="UTF-8"?>\r\n \
            <StyledLayerDescriptor version="1.0.0" \r\n \
                xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" \r\n \
                xmlns="http://www.opengis.net/sld" \r\n \
                xmlns:ogc="http://www.opengis.net/ogc" \r\n \
                xmlns:xlink="http://www.w3.org/1999/xlink" \r\n \
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n \
                <NamedLayer>\r\n \
                    <Name>default_line</Name>\r\n \
                    <UserStyle>\r\n \
                        <FeatureTypeStyle>\r\n \
                            <Rule>\r\n \
                                <LineSymbolizer>\r\n \
                                    <Stroke>\r\n \
                                        <CssParameter name="stroke">{0}</CssParameter>\r\n \
                                        <CssParameter name="stroke-width">{1}</CssParameter>\r\n \
                                    </Stroke>\r\n \
                                </LineSymbolizer>\r\n \
                            </Rule>\r\n \
                        </FeatureTypeStyle>\r\n \
                    </UserStyle>\r\n \
                </NamedLayer>\r\n\
            </StyledLayerDescriptor>'.format(color, width)
        return style

    def __getPolygonStyle(self, styleParas):
        """
        生成多边形类型的样式xml
        styleParas：样式参数 {fill_color:"#AAAAAA", outline_color:"#000000", outline_width:1}
        return xml
        """

        fill_color = "#AAAAAA"
        if "fill_color" in styleParas:
            fill_color = styleParas["fill_color"]

        outline_color = "#000000"
        if "outline_color" in styleParas:
            outline_color = styleParas["outline_color"]

        outline_width = 1
        if "outline_width" in styleParas:
            outline_width = styleParas["outline_width"]

        style = '<?xml version="1.0" encoding="UTF-8"?>\r\n \
            <StyledLayerDescriptor version="1.0.0" \r\n \
                xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" \r\n \
                xmlns="http://www.opengis.net/sld" \r\n \
                xmlns:ogc="http://www.opengis.net/ogc" \r\n \
                xmlns:xlink="http://www.w3.org/1999/xlink" \r\n \
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n \
                <NamedLayer>\r\n \
                    <Name>default_polygon</Name>\r\n \
                    <UserStyle>\r\n \
                        <FeatureTypeStyle>\r\n \
                            <Rule>\r\n \
                                <PolygonSymbolizer>\r\n \
                                    <Fill>\r\n \
                                        <CssParameter name="fill">{0}</CssParameter>\r\n \
                                    </Fill>\r\n \
                                    <Stroke>\r\n \
                                        <CssParameter name="stroke">{1}</CssParameter>\r\n \
                                        <CssParameter name="stroke-width">{2}</CssParameter>\r\n \
                                    </Stroke>\r\n \
                                </PolygonSymbolizer>\r\n \
                            </Rule>\r\n \
                        </FeatureTypeStyle>\r\n \
                    </UserStyle>\r\n \
                </NamedLayer>\r\n\
            </StyledLayerDescriptor>'.format(fill_color, outline_color, outline_width)
        return style

    def getStyle(self, workspaceName, styleName):
        """
        通过名称获取样式
        workspaceName： 样式所在的工作空间的名称
        styleName：样式的名称
        return Style
        """

        return self.__cat.get_style(styleName, workspaceName)

    def isStyleExist(self, workspaceName, styleName):
        """
        判断样式是否存在
        workspaceName： 样式所在的工作空间的名称
        styleName：样式的名称
        return True-存在;False-不存在
        """

        res = self.getStyle(workspaceName, styleName)
        if res == None:
            return False
        else:
            return True

    def createStyle(self, workspaceName, styleName, styleType, styleParas):
        """
        创建样式
        workspaceName： 样式所在的工作空间的名称
        styleName：样式的名称
        styleType：样式的类型 point/polyline/line/polygon
        styleParas: 样式的参数, 
                   point-{type:circle/rectangle/star, color:"#000000", transparency:0.5, size:10}
                   polyline/line-{color:"#000000", width:1}
                   polygon-{fill_color:"#AAAAAA", outline_color:"#000000", outline_width:1}
        return {
            status: 状态，success-创建成功;fail-创建失败
            info: 信息, success-""; fail-不支持的样式类型
            data: Style
        }
        """

        res = {
            "status": "fail",
            "info": "",
            "data": None
        }

        styleData = None
        if styleType == "point":
            styleData = self.__getPointStyle(styleParas)
        elif styleType == "polyline" or styleType == "line":
            styleData = self.__getPolylineStyle(styleParas)
        elif styleType == "polygon":
            styleData = self.__getPolygonStyle(styleParas)
        else:
            res["info"] = "不支持的样式类型"
            return res

        style = self.__cat.create_style(styleName, styleData, overwrite=True, workspace=workspaceName)
        res["status"] = "success"
        res["data"] = style
        return res

    def deleteStyle(self, workspaceName, styleName):
        """
        删除样式
        workspaceName： 样式所在的工作空间的名称
        styleName：样式的名称
        """

        style = self.getStyle(workspaceName, styleName)
        if style != None:
            self.__cat.delete(style, None, True)

    def updateStyle(self, workspaceName, styleName, styleType, styleParas):
        """
        更新样式
        workspaceName： 样式所在的工作空间的名称
        styleName：样式的名称
        styleType：样式的类型 point/polyline/line/polygon
        styleParas: 样式的参数, 
                   point-{type:circle/rectangle/star, color:"#000000", transparency:0.5, size:10}
                   polyline/line-{color:"#000000", width:1}
                   polygon-{fill_color:"#AAAAAA", outline_color:"#000000", outline_width:1}
        return {
            status: 状态，success-创建成功;fail-创建失败
            info: 信息, success-""; fail-样式不存在/不支持的样式类型
            data: Style
        }
        """

        res = {
            "status": "fail",
            "info": "",
            "data": None
        }

        if not self.isStyleExist(workspaceName, styleName):
            res["info"] = "样式不存在：{0}".format(styleName)
            return res

        # 获取样式
        style = self.getStyle(workspaceName, styleName)
        
        if styleType == "point":
            data = self.__getPointStyle(styleParas)
        elif styleType == "polyline" or styleType == "line":
            data = self.__getPolylineStyle(styleParas)
        elif styleType == "polygon":
            data = self.__getPolygonStyle(styleParas)
        else:
            res["info"] = "不支持的样式类型"
            return res
        
        style.update_body(data)
        res["status"] = "success"
        return res
    
    def getWorkSpaces(self):
        return self.__cat.get_workspaces()