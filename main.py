import json
from pprint import pprint

from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient import errors


class GCPSDKObject():
    SERVICE_ACCOUNT_FILE = '/path/to/service-account-file.json'

    def get_compute_client(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE)
        service = discovery.build('compute', 'v1', credentials=credentials)
        return service

    def backend_buckets_list(self, project_name: str):
        """
        列出GCS后端
        """
        service = self.get_compute_client()
        result = list()
        request = service.backendBuckets().list(project=project_name)

        while request is not None:
            try:
                response = request.execute()
            except errors.HttpError as err:
                print(err._get_reason())
                raise err

            for backend_service in response['items']:
                pprint(backend_service)
                result.append(backend_service)

            request = service.backendServices().list_next(previous_request=request, previous_response=response)

        return result

    def backend_buckets_create(self, project_name: str, backend_bucket_name: str, gcs_bucket_name: str):
        """
        创建 backend GCS 后端
        :param project_name:  project_id 或者 project_name
        :param backend_bucket_name:  新创建的 backend 名称
        :param gcs_bucket_name:  GCP侧 cloud storage 中的bucket名称，一定要和实际的一致
        :return:
        """
        # api: https://cloud.google.com/compute/docs/reference/rest/v1/backendBuckets/insert
        service = self.get_compute_client()

        body = {
            "name": backend_bucket_name,
            "bucketName": gcs_bucket_name,
            "enableCdn": True
        }

        request = service.backendBuckets().insert(project=project_name, body=body)

        try:
            response = request.execute()
            pprint(response)
            return response
        except errors.HttpError as err:
            # Something went wrong, print out some information.
            print('There was an error creating the model. Check the details:')
            print(err._get_reason())
            raise err

    def backend_gcs_url_maps_list(self, project_name: str):
        service = self.get_compute_client()
        result = list()
        request = service.urlMaps().list(project=project_name)
        while request is not None:
            try:
                response = request.execute()
            except errors.HttpError as err:
                # Something went wrong, print out some information.
                print('There was an error creating the model. Check the details:')
                print(err._get_reason())
                raise err

            for url_map in response['items']:
                pprint(url_map)
                result.append(url_map)

            request = service.urlMaps().list_next(previous_request=request, previous_response=response)

        return result

    def backend_gcs_url_maps_create(self, project_name: str, url_map_name: str, backend_or_service_name: str,
                                    is_bucket=True):
        """
         配置GCS后端 网址映射
        :param project_name:
        :param url_map_name:
        :param backend_or_service_name:
        :param is_bucket: default=True
        :return:
        """
        # api: https://cloud.google.com/compute/docs/reference/rest/v1/urlMaps/insert

        service = self.get_compute_client()
        if is_bucket:
            service_url = f"compute/v1/projects/{project_name}/global/backendBuckets/{backend_or_service_name}"
        else:
            service_url = f"compute/v1/projects/{project_name}/global/backendServices/{backend_or_service_name}"
        body = {
            "name": url_map_name,
            "defaultService": service_url,
        }
        request = service.urlMaps().insert(project=project_name, body=body)

        try:
            response = request.execute()
            pprint(response)
            return response
        except errors.HttpError as err:
            print(err._get_reason())
            raise err

    def compute_global_addresses_list(self, project_name: str):
        service = self.get_compute_client()
        result = list()
        request = service.globalAddresses().list(project=project_name)
        while request is not None:
            try:
                response = request.execute()
            except errors.HttpError as err:
                print(err._get_reason())
                raise err

            for address in response['items']:
                pprint(address)
                result.append(address)

            request = service.globalAddresses().list_next(previous_request=request, previous_response=response)
        return result

    def compute_global_addresses_create(self, project_name: str, address_name: str, ip_type: str = "IPV4"):
        """
        创建全局静态外部 IP 地址
        :param project_name:
        :param address_name:
        :param ip_type:
        :return:
        """
        service = self.get_compute_client()
        body = {
            "name": address_name,
            "ipVersion": ip_type,
            "addressType": "EXTERNAL"
        }
        request = service.globalAddresses().insert(project=project_name, body=body)

        try:
            response = request.execute()
            pprint(response)
            return response
        except errors.HttpError as err:
            print(err._get_reason())
            raise err

    def target_http_proxies_create(self, project_name: str, proxy_name: str, url_map_name: str):
        """
        创建代理 proxy
        创建目标 HTTP 代理以将请求路由到您的网址映射
        """

        service = self.get_compute_client()
        body = {
            "name": proxy_name,
            "urlMap": url_map_name
        }

        request = service.targetHttpProxies().insert(project=project_name, body=body)
        try:
            response = request.execute()
            pprint(response)
            return response
        except errors.HttpError as err:
            print(err._get_reason())
            raise err

    def target_https_proxies_create(self, project_name: str, proxy_name: str, url_map_name: str, cert_name: str):
        """
        创建代理 proxy 使用ssl证书
        """

        service = self.get_compute_client()
        body = {
            "name": proxy_name,
            "urlMap": url_map_name,
            "sslCertificates": [cert_name]
        }

        request = service.targetHttpsProxies().insert(project=project_name, body=body)
        try:
            response = request.execute()
            pprint(response)
            return response
        except errors.HttpError as err:
            print(err._get_reason())
            raise err

    def ssl_certificates_create(self, cert_name: str, certificate: str, private_key: str, description: str = "",
                                project_name: str = "spoton-project"):
        """
        创建证书
            gcloud compute ssl-certificates list
        """
        body = {"name": cert_name, "certificate": certificate, "privateKey": private_key, "description": description}
        compute = self.get_compute_client()
        request = compute.sslCertificates().insert(project=project_name, body=body)
        try:
            response = request.execute()
            return response
        except errors.HttpError as err:
            print(err._get_reason())
            raise err

    def global_forwarding_rules_create(self, project_name: str, forwarding_rule_name: str, address_name: str, port: int,
                                       proxy_name: str):
        """
        前端配置
        """
        service = self.get_compute_client()

        body = {
            "name": forwarding_rule_name,
            "IPAddress": address_name,
            "target": proxy_name,
            "ports": [
                str(port)
            ]
        }

        request = service.globalForwardingRules().insert(project=project_name, body=body)
        try:
            response = request.execute()
            return response
        except errors.HttpError as err:
            print(err._get_reason())
            raise err


def create_cdn_with_gcs_with_api(cdn_gcs_config):
    """ GCS 方式 cdn
    """

    # 初始化工具类
    gcp_sdk_obj = GCPSDKObject()
    project_name = cdn_gcs_config["project_name"]

    # Backend configuration
    backend_config = cdn_gcs_config.get("backend_bucket_params")

    # 创建backend GCS 后端
    gcp_sdk_obj.backend_buckets_create(project_name, backend_config.get("backend_bucket_name"),
                                       backend_config.get("gcs_bucket_name"))

    # 创建 URL MAP
    glb_config = cdn_gcs_config.get("url_map_params")
    glb_name = glb_config.get("url_map_name")
    gcp_sdk_obj.backend_gcs_url_maps_create(project_name, glb_name, backend_config.get("backend_bucket_name"))

    # Frontend configuration
    front_http_config = cdn_gcs_config.get("frontend_http_params")
    front_https_config = cdn_gcs_config.get("frontend_https_params")

    # 生成静态IP
    gcp_sdk_obj.compute_global_addresses_create(project_name, front_http_config.get("address_name"),
                                                front_http_config.get("ip_type"))

    # 创建 target_proxy
    gcp_sdk_obj.target_http_proxies_create(project_name, front_http_config["target_proxy"]["target_proxy_name"],
                                           glb_name)

    if "https" in cdn_gcs_config.get("domain_protocol"):
        # 创建证书
        gcp_sdk_obj.ssl_certificates_create(front_https_config["target_proxy"]["cert_name"],
                                            front_https_config["target_proxy"]["cert_certificate"],
                                            front_https_config["target_proxy"]["cert_private_key"],
                                            project_name=project_name)

        # 创建 target_proxy SSL 代理
        gcp_sdk_obj.target_https_proxies_create(project_name,
                                                front_https_config["target_proxy"]["target_proxy_name"],
                                                glb_name,
                                                front_https_config["target_proxy"]["cert_name"])

    # 添加前端
    if cdn_gcs_config.get("domain_protocol") == "http":
        gcp_sdk_obj.global_forwarding_rules_create(project_name,
                                                   front_http_config.get("forwarding_rule_name"),
                                                   front_http_config.get("address_name"),
                                                   front_http_config.get("port", 80),
                                                   front_http_config["target_proxy"]["target_proxy_name"])

    elif cdn_gcs_config.get("domain_protocol") == "https":
        gcp_sdk_obj.global_forwarding_rules_create(project_name,
                                                   front_https_config.get("forwarding_rule_name"),
                                                   front_https_config.get("address_name"),
                                                   front_https_config.get("port", 443),
                                                   front_https_config["target_proxy"]["target_proxy_name"])

    elif cdn_gcs_config.get("domain_protocol") == "http-https":
        gcp_sdk_obj.global_forwarding_rules_create(project_name,
                                                   front_http_config.get("forwarding_rule_name"),
                                                   front_http_config.get("address_name"),
                                                   front_http_config.get("port", 80),
                                                   front_http_config["target_proxy"]["target_proxy_name"])
        gcp_sdk_obj.global_forwarding_rules_create(project_name,
                                                   front_https_config.get("forwarding_rule_name"),
                                                   front_https_config.get("address_name"),
                                                   front_https_config.get("port", 443),
                                                   front_https_config["target_proxy"]["target_proxy_name"])


if __name__ == '__main__':
    cdn_gcs_config = {
        "project_name": "",
        "domain_protocol": "",
        "backend_bucket_params": {
            "backend_bucket_name": "string",
            "gcs_bucket_name": "string"
        },
        "url_map_params": {
            "url_map_name": "string",
            "url_maps": []
        },
        "frontend_http_params": {
            "forwarding_rule_name": "string",
            "address_name": "string",
            "ip_type": "string",
            "protocol": "string",
            "port": 0,
            "target_proxy": {
                "target_proxy_name": "string"
            }
        },
        "frontend_https_params": {
            "forwarding_rule_name": "string",
            "address_name": "string",
            "ip_type": "string",
            "protocol": "string",
            "port": 0,
            "target_proxy": {
                "target_proxy_name": "string",
                "cert_name": "string",
                "cert_certificate": "string",
                "cert_private_key": "string"
            }
        }
    }

    create_cdn_with_gcs_with_api(cdn_gcs_config)
