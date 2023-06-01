# geoserver
基于```geoserver-restconfig```封装的```geoserver```发布服务类，支持```shp```和```tif```两种数据

# 文件说明

```GeoServerCatalog.py``` 是基于```geoserver.Catalog```的派生类，用于扩展基类的```create_coveragestore```函数，使其支持"ImagePyramid"类型，该类型可发布大型TIFF文件（>2GB）

```GeoServerService.py``` 是基于```GeoServerCatalog```封装的```geoserver```发布服务类，可用于创建工作空间、发布```SHP```、发布```TIFF```、发布金字塔型```TIFF```、修改图层样式等操作

```gdal_retile.py```      是对```TIFF```文件进行金字塔切片的功能文件

```demo_```开头的文件是上述服务类的使用案例，分别为发布shp、发布普通tif(<2GB)、发布大型tif(>=2GB)的案例
# 部署

## 安装python
```windows```系统可安装```3.11```及以下的版本
```linux```系统可安装```3.9```及以下的版本

## 安装geoserver-restconfig

这是控制```geoserver```的核心库

```pip install geoserver-restconfig```

## 安装gdal

windows版本下载地址
https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal

linux版本下载地址
https://sourceforge.net/projects/gdal-wheels-for-linux/files/

下载的是```whl```类型的，可通过```pip```直接安装，由于```gdal```支持的```python```版本不同，所以之前```python```的安装版本推荐不同

## geoserver安装ImagePyramid插件
如果你已安装或者不打算使用发布```金字塔切片TIFF```服务（普通的TIF发布服务在文件<2GB时访问效率还可以，超过2GB效率很低。提前对其进行切片，并用金字塔服务进行访问可提升访问效率），可忽略此步骤

在下面的链接找到对应的```geoserver```版本，然后进入```extensions```下载```geoserver-xxx-pyramid-plugin.zip```

https://sourceforge.net/projects/geoserver/files/GeoServer/

下载后解压，将```gt-imagepyramid-xx.jar```文件拷贝到```geoserverPath\webapps\geoserver\WEB-INF\lib```下，重启```geoserver```服务即可
