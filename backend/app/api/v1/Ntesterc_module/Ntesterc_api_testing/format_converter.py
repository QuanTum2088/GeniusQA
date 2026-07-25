#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
from typing import Dict, Any, List, Optional


class FormatConverter:
    """格式转换器"""
    
    @staticmethod
    def detect_format(data: Dict[str, Any]) -> str:
        """
        检测导入数据的格式
        返回: 'internal', 'openapi', 'swagger', 'apifox', 'postman', 'unknown'
        """
        # 检查是否为内部格式
        if data.get('type') in ['api_project', 'collection', 'environments']:
            return 'internal'
        
        # 检查是否为OpenAPI 3.x
        if 'openapi' in data and data['openapi'].startswith('3.'):
            return 'openapi'
        
        # 检查是否为Swagger 2.0
        if 'swagger' in data and data['swagger'] == '2.0':
            return 'swagger'
        
        # 检查是否为Apifox格式（Apifox导出的OpenAPI格式会有特殊标识）
        if 'openapi' in data and 'info' in data:
            info = data.get('info', {})
            if 'x-apifox' in info or 'x-apifox-folder' in data:
                return 'apifox'
        
        # 检查是否为Postman格式
        if 'info' in data and 'schema' in data.get('info', {}):
            schema = data['info']['schema']
            if 'postman' in schema.lower():
                return 'postman'
        
        return 'unknown'
    
    @staticmethod
    def convert_to_internal(data: Dict[str, Any], format_type: str = None) -> Dict[str, Any]:
        """
        将外部格式转换为内部格式
        """
        if format_type is None:
            format_type = FormatConverter.detect_format(data)
        
        if format_type == 'internal':
            return data
        elif format_type in ['openapi', 'swagger', 'apifox']:
            return FormatConverter._convert_openapi_to_internal(data)
        elif format_type == 'postman':
            return FormatConverter._convert_postman_to_internal(data)
        else:
            raise ValueError(f"不支持的格式: {format_type}")
    
    @staticmethod
    def _convert_openapi_to_internal(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将OpenAPI/Swagger/Apifox格式转换为内部格式
        """
        info = data.get('info', {})
        servers = data.get('servers', [])
        paths = data.get('paths', {})
        
        # 获取基础URL
        base_url = ''
        if servers and len(servers) > 0:
            base_url = servers[0].get('url', '')
        
        # 创建内部格式
        internal_data = {
            'version': '1.0',
            'type': 'api_project',
            'project': {
                'name': info.get('title', 'Imported API Project'),
                'description': info.get('description', ''),
                'project_type': 'HTTP',
                'base_url': base_url
            },
            'collections': [],
            'requests': []
        }
        
        # 处理tags作为集合
        tags = data.get('tags', [])
        tag_map = {}  # tag名称 -> collection_id映射
        
        for idx, tag in enumerate(tags):
            collection_id = f"collection_{idx}"
            collection_data = {
                'id': collection_id,
                'name': tag.get('name', f'Collection {idx}'),
                'description': tag.get('description', ''),
                'parent_id': None,
                'order_num': idx
            }
            internal_data['collections'].append(collection_data)
            tag_map[tag['name']] = collection_id
        
        # 如果没有tags，创建一个默认集合
        if not tags:
            default_collection_id = 'collection_default'
            internal_data['collections'].append({
                'id': default_collection_id,
                'name': 'Default',
                'description': 'Default collection',
                'parent_id': None,
                'order_num': 0
            })
            tag_map['default'] = default_collection_id
        
        # 处理paths作为请求
        request_order = 0
        for path, path_item in paths.items():
            # 遍历HTTP方法
            for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                if method not in path_item:
                    continue
                
                operation = path_item[method]
                
                # 确定请求所属的集合
                operation_tags = operation.get('tags', [])
                collection_id = tag_map.get(operation_tags[0] if operation_tags else 'default', 
                                           tag_map.get('default', 'collection_default'))
                
                # 提取参数
                params = {}
                headers = {}
                body = None
                
                # 处理parameters
                parameters = operation.get('parameters', [])
                for param in parameters:
                    param_name = param.get('name', '')
                    param_in = param.get('in', '')
                    param_schema = param.get('schema', {})
                    param_type = param_schema.get('type', 'string')
                    param_example = param.get('example', param_schema.get('example', ''))
                    param_description = param.get('description', '')
                    
                    if param_in == 'query':
                        # 简化格式：直接存储值
                        params[param_name] = str(param_example) if param_example else ''
                    elif param_in == 'header':
                        headers[param_name] = str(param_example) if param_example else ''
                    elif param_in == 'path':
                        # path参数通常在URL中，这里记录到params中
                        params[param_name] = str(param_example) if param_example else ''
                
                # 处理requestBody
                request_body = operation.get('requestBody', {})
                if request_body:
                    content = request_body.get('content', {})
                    # 优先处理JSON格式
                    if 'application/json' in content:
                        json_content = content['application/json']
                        schema = json_content.get('schema', {})
                        example = json_content.get('example', schema.get('example', {}))
                        
                        # 如果有example，使用example；否则根据schema生成示例
                        if example:
                            body = example
                        else:
                            body = FormatConverter._generate_example_from_schema(schema)
                    elif 'application/x-www-form-urlencoded' in content:
                        form_content = content['application/x-www-form-urlencoded']
                        schema = form_content.get('schema', {})
                        body = FormatConverter._generate_example_from_schema(schema)
                
                # 创建请求
                request_data = {
                    'collection_id': collection_id,
                    'name': operation.get('summary', operation.get('operationId', f'{method.upper()} {path}')),
                    'description': operation.get('description', ''),
                    'request_type': 'HTTP',
                    'method': method.upper(),
                    'url': path,
                    'headers': headers,
                    'params': params,
                    'body': body,
                    'auth': None,
                    'pre_request_script': '',
                    'post_request_script': '',
                    'assertions': [],
                    'order_num': request_order
                }
                
                internal_data['requests'].append(request_data)
                request_order += 1
        
        return internal_data
    
    @staticmethod
    def _generate_example_from_schema(schema: Dict[str, Any]) -> Any:
        """
        根据JSON Schema生成示例数据
        """
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            example = {}
            for prop_name, prop_schema in properties.items():
                example[prop_name] = FormatConverter._generate_example_from_schema(prop_schema)
            return example
        
        elif schema_type == 'array':
            items = schema.get('items', {})
            return [FormatConverter._generate_example_from_schema(items)]
        
        elif schema_type == 'string':
            return schema.get('example', schema.get('default', ''))
        
        elif schema_type == 'integer':
            return schema.get('example', schema.get('default', 0))
        
        elif schema_type == 'number':
            return schema.get('example', schema.get('default', 0.0))
        
        elif schema_type == 'boolean':
            return schema.get('example', schema.get('default', False))
        
        else:
            return None
    
    @staticmethod
    def _convert_postman_to_internal(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将Postman格式转换为内部格式
        """
        info = data.get('info', {})
        items = data.get('item', [])
        
        internal_data = {
            'version': '1.0',
            'type': 'api_project',
            'project': {
                'name': info.get('name', 'Imported Postman Collection'),
                'description': info.get('description', ''),
                'project_type': 'HTTP',
                'base_url': ''
            },
            'collections': [],
            'requests': []
        }
        
        # 递归处理items（可能是文件夹或请求）
        def process_items(items: List[Dict], parent_id: Optional[str] = None, level: int = 0):
            for idx, item in enumerate(items):
                # 如果item有request字段，说明是请求
                if 'request' in item:
                    request = item['request']
                    url_obj = request.get('url', {})
                    
                    # 处理URL
                    if isinstance(url_obj, str):
                        url = url_obj
                    else:
                        url = url_obj.get('raw', '')
                    
                    # 处理headers
                    headers = {}
                    for header in request.get('header', []):
                        if not header.get('disabled', False):
                            headers[header['key']] = header.get('value', '')
                    
                    # 处理body
                    body = None
                    body_obj = request.get('body', {})
                    if body_obj:
                        mode = body_obj.get('mode', 'raw')
                        if mode == 'raw':
                            body = body_obj.get('raw', '')
                        elif mode == 'formdata':
                            body = {}
                            for form_item in body_obj.get('formdata', []):
                                body[form_item['key']] = form_item.get('value', '')
                    
                    request_data = {
                        'collection_id': parent_id or 'collection_default',
                        'name': item.get('name', 'Unnamed Request'),
                        'description': item.get('description', ''),
                        'request_type': 'HTTP',
                        'method': request.get('method', 'GET'),
                        'url': url,
                        'headers': headers,
                        'params': {},
                        'body': body,
                        'auth': None,
                        'pre_request_script': '',
                        'post_request_script': '',
                        'assertions': [],
                        'order_num': len(internal_data['requests'])
                    }
                    internal_data['requests'].append(request_data)
                
                # 如果item有item字段，说明是文件夹
                elif 'item' in item:
                    collection_id = f"collection_{len(internal_data['collections'])}"
                    collection_data = {
                        'id': collection_id,
                        'name': item.get('name', f'Folder {idx}'),
                        'description': item.get('description', ''),
                        'parent_id': parent_id,
                        'order_num': len(internal_data['collections'])
                    }
                    internal_data['collections'].append(collection_data)
                    
                    # 递归处理子项
                    process_items(item['item'], collection_id, level + 1)
        
        # 创建默认集合
        if items:
            default_collection_id = 'collection_default'
            internal_data['collections'].append({
                'id': default_collection_id,
                'name': 'Default',
                'description': 'Default collection',
                'parent_id': None,
                'order_num': 0
            })
            
            process_items(items)
        
        return internal_data


# 创建转换器实例
format_converter = FormatConverter()
