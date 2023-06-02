import os
from geoserver.catalog import Catalog, ConflictingDataError, _name, FailedRequestError
from geoserver.store import UnsavedCoverageStore
from geoserver.support import build_url

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

class GeoServerCatalog(Catalog):
    """
    geoserver.Catalog的派生类
    用于扩展基类的create_coveragestore函数，使其支持"ImagePyramid"类型
    """
    def __init__(self, service_url, username="admin", password="geoserver", validate_ssl_certificate=True, access_token=None, retries=3, backoff_factor=0.9):
        super().__init__(service_url, username, password, validate_ssl_certificate, access_token, retries, backoff_factor)

    def create_coveragestore(self, name, workspace=None, path=None, type='GeoTIFF',
                             create_layer=True, layer_name=None, source_name=None, upload_data=False, contet_type="image/tiff",
                             overwrite=False):
        """
        Create a coveragestore for locally hosted rasters.
        If create_layer is set to true, will create a coverage/layer.
        layer_name and source_name are only used if create_layer ia enabled. If not specified, the raster name will be used for both.
        """
        if path is None:
            raise Exception('You must provide a full path to the raster')

        if layer_name is not None and ":" in layer_name:
            ws_name, layer_name = layer_name.split(':')

        allowed_types = [
            'ImageMosaic',
            'GeoTIFF',
            'Gtopo30',
            'WorldImage',
            'AIG',
            'ArcGrid',
            'DTED',
            'EHdr',
            'ERDASImg',
            'ENVIHdr',
            'GeoPackage (mosaic)',
            'NITF',
            'RPFTOC',
            'RST',
            'VRT',
            'ImagePyramid'
        ]

        if type is None:
            raise Exception('Type must be declared')
        elif type not in allowed_types:
            raise Exception(f"Type must be one of {', '.join(allowed_types)}")

        if workspace is None:
            workspace = self.get_default_workspace()
        workspace = _name(workspace)

        if not overwrite:
            stores = self.get_stores(names=name, workspaces=[workspace])
            if len(stores) > 0:
                msg = f"There is already a store named {name} in workspace {workspace}"
                raise ConflictingDataError(msg)

        if upload_data is False:
            cs = UnsavedCoverageStore(self, name, workspace)
            cs.type = type
            cs.url = path if path.startswith("file:") else f"file:{path}"
            self.save(cs)

            if create_layer:
                if layer_name is None:
                    layer_name = os.path.splitext(os.path.basename(path))[0]
                if source_name is None:
                    source_name = os.path.splitext(os.path.basename(path))[0]

                data = f"<coverage><name>{layer_name}</name><nativeName>{source_name}</nativeName></coverage>"
                url = f"{self.service_url}/workspaces/{workspace}/coveragestores/{name}/coverages.xml"
                headers = {"Content-type": "application/xml"}

                resp = self.http_request(url, method='post', data=data, headers=headers)
                if resp.status_code != 201:
                    raise FailedRequestError('Failed to create coverage/layer {} for : {}, {}'.format(layer_name, name,
                                                                                                      resp.status_code, resp.text))
                self._cache.clear()
                return self.get_resources(names=layer_name, workspaces=[workspace])[0]
        else:
            data = open(path, 'rb')
            params = {"configure": "first", "coverageName": name}
            url = build_url(
                self.service_url,
                [
                    "workspaces",
                    workspace,
                    "coveragestores",
                    name,
                    f"file.{type.lower()}"
                ],
                params
            )

            headers = {"Content-type": contet_type}
            resp = self.http_request(url, method='put', data=data, headers=headers)

            if hasattr(data, "close"):
                data.close()

            if resp.status_code != 201:
                raise FailedRequestError('Failed to create coverage/layer {} for : {}, {}'.format(layer_name, name, resp.status_code, resp.text))

        return self.get_stores(names=name, workspaces=[workspace])[0]
    
    def setup_connection(self, retries=3, backoff_factor=0.9):
        self.client = requests.session()
        self.client.verify = self.validate_ssl_certificate
        parsed_url = urlparse(self.service_url)

        try:
            retry = Retry(
                total = retries or self.retries,
                status = retries or self.retries,
                read = retries or self.retries,
                connect = retries or self.retries,
                backoff_factor = backoff_factor or self.backoff_factor,
                status_forcelist = [502, 503, 504],
                allowed_methods = set(['HEAD', 'TRACE', 'GET', 'PUT', 'POST', 'OPTIONS', 'DELETE'])
            ) # allowed_methods : requests > 2.22.0
        except TypeError:
            retry = Retry(
                total = retries or self.retries,
                status = retries or self.retries,
                read = retries or self.retries,
                connect = retries or self.retries,
                backoff_factor = backoff_factor or self.backoff_factor,
                status_forcelist = [502, 503, 504],
                method_whitelist = set(['HEAD', 'TRACE', 'GET', 'PUT', 'POST', 'OPTIONS', 'DELETE'])
            ) # method_whitelist : requests <= 2.22.0

        self.client.mount(f"{parsed_url.scheme}://", HTTPAdapter(max_retries=retry))
