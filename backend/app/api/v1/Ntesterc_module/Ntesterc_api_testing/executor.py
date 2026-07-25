#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
import re
import time
import json
from typing import Dict, Any, Optional, List
import httpx
from jsonpath_ng import parse as jsonpath_parse
from sqlalchemy.ext.asyncio import AsyncSession
from .crud import APIEnvironmentCRUD, APIRequestCRUD
from .model import APIRequestHistoryModel


class ScriptExecutor:
    """脚本执行器（安全沙箱）"""
    
    @staticmethod
    def execute_script(
        script: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行Python脚本（受限环境）"""
        if not script or not script.strip():
            return context
        
        # 创建受限的执行环境
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sorted': sorted,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'isinstance': isinstance,
                'type': type,
                'json': json,
                're': re,
            },
            'context': context,
            'env': context.get('env', {}),
            'request': context.get('request', {}),
            'response': context.get('response', {}),
        }
        
        try:
            # 执行脚本
            exec(script, safe_globals)
            
            # 更新上下文
            context['env'] = safe_globals.get('env', context.get('env', {}))
            
            return context
        
        except Exception as e:
            context['script_error'] = str(e)
            return context


class VariableResolver:
    """变量解析器"""
    
    @staticmethod
    def resolve_variables(text: str, variables: Dict[str, Any]) -> str:
        """解析变量 {{variable}}"""
        if not text or not variables:
            return text
        
        # 匹配 {{variable}} 格式
        pattern = r'\{\{(\w+)\}\}'
        
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))
        
        return re.sub(pattern, replace_var, text)
    
    @staticmethod
    def resolve_dict_variables(data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """解析字典中的变量"""
        if not data or not variables:
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = VariableResolver.resolve_variables(value, variables)
            elif isinstance(value, dict):
                result[key] = VariableResolver.resolve_dict_variables(value, variables)
            elif isinstance(value, list):
                result[key] = [
                    VariableResolver.resolve_variables(item, variables) if isinstance(item, str)
                    else VariableResolver.resolve_dict_variables(item, variables) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result


class AssertionEngine:
    """断言引擎"""
    
    @staticmethod
    def execute_assertions(
        assertions: List[Dict[str, Any]],
        response_data: Dict[str, Any],
        status_code: int,
        response_time: float
    ) -> List[Dict[str, Any]]:
        """执行断言"""
        results = []
        
        for assertion in assertions:
            assertion_type = assertion.get('type')
            operator = assertion.get('operator')
            expected = assertion.get('expected')
            
            result = {
                'type': assertion_type,
                'operator': operator,
                'expected': expected,
                'passed': False,
                'message': ''
            }
            
            try:
                if assertion_type == 'status_code':
                    result['actual'] = status_code
                    result['passed'] = AssertionEngine._compare(status_code, operator, expected)
                    result['message'] = f"状态码断言: {status_code} {operator} {expected}"
                
                elif assertion_type == 'response_time':
                    result['actual'] = response_time
                    result['passed'] = AssertionEngine._compare(response_time, operator, expected)
                    result['message'] = f"响应时间断言: {response_time}ms {operator} {expected}ms"
                
                elif assertion_type == 'jsonpath':
                    jsonpath = assertion.get('jsonpath')
                    jsonpath_expr = jsonpath_parse(jsonpath)
                    matches = jsonpath_expr.find(response_data)
                    
                    if matches:
                        actual_value = matches[0].value
                        result['actual'] = actual_value
                        result['passed'] = AssertionEngine._compare(actual_value, operator, expected)
                        result['message'] = f"JSONPath断言: {jsonpath} = {actual_value} {operator} {expected}"
                    else:
                        result['passed'] = False
                        result['message'] = f"JSONPath未找到: {jsonpath}"
                
                elif assertion_type == 'body_contains':
                    body_str = json.dumps(response_data)
                    result['passed'] = expected in body_str
                    result['message'] = f"响应体包含断言: {'通过' if result['passed'] else '失败'}"
                
                elif assertion_type == 'header':
                    header_name = assertion.get('header_name')
                    header_value = response_data.get('headers', {}).get(header_name)
                    result['actual'] = header_value
                    result['passed'] = AssertionEngine._compare(header_value, operator, expected)
                    result['message'] = f"响应头断言: {header_name} = {header_value} {operator} {expected}"
                
            except Exception as e:
                result['passed'] = False
                result['message'] = f"断言执行失败: {str(e)}"
            
            results.append(result)
        
        return results
    
    @staticmethod
    def _compare(actual, operator: str, expected) -> bool:
        """比较操作"""
        if operator == 'equals' or operator == '==':
            return actual == expected
        elif operator == 'not_equals' or operator == '!=':
            return actual != expected
        elif operator == 'greater_than' or operator == '>':
            return float(actual) > float(expected)
        elif operator == 'less_than' or operator == '<':
            return float(actual) < float(expected)
        elif operator == 'greater_or_equal' or operator == '>=':
            return float(actual) >= float(expected)
        elif operator == 'less_or_equal' or operator == '<=':
            return float(actual) <= float(expected)
        elif operator == 'contains':
            return expected in str(actual)
        elif operator == 'not_contains':
            return expected not in str(actual)
        elif operator == 'starts_with':
            return str(actual).startswith(str(expected))
        elif operator == 'ends_with':
            return str(actual).endswith(str(expected))
        else:
            return False


class RequestExecutor:
    """请求执行器"""
    
    @staticmethod
    async def execute_request(
        db: AsyncSession,
        request_id: int,
        environment_id: Optional[int],
        user_id: int
    ) -> Dict[str, Any]:
        """执行API请求"""
        # 创建CRUD实例
        api_request_crud = APIRequestCRUD(db)
        api_environment_crud = APIEnvironmentCRUD(db)
        
        # 获取请求信息
        request = await api_request_crud.get_by_id_crud(request_id)
        if not request:
            raise ValueError("请求不存在")
        
        # 获取项目ID（通过collection_id -> api_project_id -> project_id）
        from .crud import APICollectionCRUD, APIProjectCRUD
        collection_crud = APICollectionCRUD(db)
        api_project_crud = APIProjectCRUD(db)
        
        collection = await collection_crud.get_by_id_crud(request.collection_id)
        api_project = await api_project_crud.get_by_id_crud(collection.api_project_id) if collection else None
        project_id = api_project.project_id if api_project else None
        
        # 获取环境变量
        variables = {}
        environment_name = None
        if environment_id:
            environment = await api_environment_crud.get_by_id_crud(environment_id)
            if environment and environment.variables:
                variables = environment.variables
                environment_name = environment.name
        
        # 创建执行上下文
        context = {
            'env': variables.copy(),
            'request': {},
            'response': {},
            'script_error': None
        }
        
        # 执行前置操作
        if request.pre_request_script:

            if isinstance(request.pre_request_script, str):
                operations = [{'type': 'script', 'script': request.pre_request_script, 'enabled': True}]
            else:
                operations = request.pre_request_script
            
            from .operations import OperationExecutor
            context = await OperationExecutor.execute_operations(
                db=db,
                operations=operations,
                context=context,
                user_id=user_id
            )
            # 更新环境变量
            variables.update(context['env'])
        
        # 解析URL
        url = VariableResolver.resolve_variables(request.url, variables)
        
        # 解析请求头
        headers = {}
        if request.headers:
            headers = VariableResolver.resolve_dict_variables(request.headers, variables)
        
        # 解析URL参数
        params = {}
        if request.params:
            params = VariableResolver.resolve_dict_variables(request.params, variables)
        
        # 解析请求体
        body = None
        if request.body:
            if isinstance(request.body, str):
                # JSON字符串
                body = VariableResolver.resolve_variables(request.body, variables)
            elif isinstance(request.body, dict):
                # 字典
                body = VariableResolver.resolve_dict_variables(request.body, variables)
            else:
                body = request.body
        
        # 解析Cookies
        cookies = {}
        if request.cookies:
            cookies = VariableResolver.resolve_dict_variables(request.cookies, variables)
        
        # 获取请求设置
        verify_ssl = getattr(request, 'verify_ssl', True)
        follow_redirects = getattr(request, 'follow_redirects', True)
        timeout = getattr(request, 'timeout', 30000) / 1000  # 转换为秒
        
        # 查找并应用SSL证书
        ssl_cert_path = None
        ssl_key_path = None
        ca_cert_path = None
        
        if project_id and verify_ssl:
            # 从URL中提取域名
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            if domain:
                # 查找匹配的证书
                from .crud import SSLCertificateCRUD
                ssl_cert_crud = SSLCertificateCRUD(db)
                certificates = await ssl_cert_crud.get_by_domain(db=db, domain=domain, project_id=project_id)
                
                # 应用证书
                import tempfile
                import os
                
                for cert in certificates:
                    if cert.cert_type == 'CA' and cert.ca_cert:
                        # 保存CA证书到临时文件
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
                            f.write(cert.ca_cert)
                            ca_cert_path = f.name
                        print(f"[DEBUG] 应用CA证书: {cert.name} -> {ca_cert_path}")
                        break  # 只使用第一个匹配的CA证书
                
                for cert in certificates:
                    if cert.cert_type == 'CLIENT' and cert.client_cert and cert.client_key:
                        # 保存客户端证书到临时文件
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False) as f:
                            f.write(cert.client_cert)
                            ssl_cert_path = f.name
                        
                        # 保存客户端私钥到临时文件
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.key', delete=False) as f:
                            f.write(cert.client_key)
                            ssl_key_path = f.name
                        
                        print(f"[DEBUG] 应用客户端证书: {cert.name} -> cert={ssl_cert_path}, key={ssl_key_path}")
                        break  # 只使用第一个匹配的客户端证书
        
        # 保存请求信息到上下文
        context['request'] = {
            'method': request.method,
            'url': url,
            'headers': headers,
            'params': params,
            'body': body,
            'cookies': cookies
        }
        
        # 执行请求
        start_time = time.time()
        error_message = None
        response_data = {}
        status_code = 0
        
        try:
            # 准备httpx客户端参数
            client_kwargs = {
                'timeout': timeout,
                'follow_redirects': follow_redirects,
                'cookies': cookies
            }
            
            # 应用SSL证书设置
            if ca_cert_path:
                # 使用CA证书验证服务器
                client_kwargs['verify'] = ca_cert_path
            elif not verify_ssl:
                # 禁用SSL验证
                client_kwargs['verify'] = False
            else:
                # 使用系统默认CA证书
                client_kwargs['verify'] = True
            
            # 应用客户端证书（双向SSL）
            if ssl_cert_path and ssl_key_path:
                client_kwargs['cert'] = (ssl_cert_path, ssl_key_path)
            
            async with httpx.AsyncClient(**client_kwargs) as client:
                # 准备请求参数
                request_kwargs = {
                    'headers': headers,
                    'params': params
                }
                
                # 根据body类型处理请求体
                if body:
                    if isinstance(body, str):
                        # JSON字符串或其他文本
                        try:
                            request_kwargs['json'] = json.loads(body)
                        except:
                            request_kwargs['data'] = body
                    elif isinstance(body, dict):
                        request_kwargs['json'] = body
                    else:
                        request_kwargs['data'] = body
                
                # 执行请求
                if request.method.upper() == 'GET':
                    response = await client.get(url, **request_kwargs)
                elif request.method.upper() == 'POST':
                    response = await client.post(url, **request_kwargs)
                elif request.method.upper() == 'PUT':
                    response = await client.put(url, **request_kwargs)
                elif request.method.upper() == 'DELETE':
                    response = await client.delete(url, **request_kwargs)
                elif request.method.upper() == 'PATCH':
                    response = await client.patch(url, **request_kwargs)
                elif request.method.upper() == 'HEAD':
                    response = await client.head(url, **request_kwargs)
                elif request.method.upper() == 'OPTIONS':
                    response = await client.options(url, **request_kwargs)
                else:
                    raise ValueError(f"不支持的请求方法: {request.method}")
                
                status_code = response.status_code
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒
                
                # 解析响应
                try:
                    response_body = response.json()
                except:
                    response_body = response.text
                
                response_data = {
                    'status_code': status_code,
                    'headers': dict(response.headers),
                    'body': response_body,
                    'response_time': response_time
                }
                
                # 保存响应信息到上下文
                context['response'] = response_data
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_message = str(e)
            response_data = {
                'error': error_message
            }
        
        finally:
            # 清理临时证书文件
            import os
            if ca_cert_path and os.path.exists(ca_cert_path):
                try:
                    os.unlink(ca_cert_path)
                    print(f"[DEBUG] 清理CA证书临时文件: {ca_cert_path}")
                except:
                    pass
            
            if ssl_cert_path and os.path.exists(ssl_cert_path):
                try:
                    os.unlink(ssl_cert_path)
                    print(f"[DEBUG] 清理客户端证书临时文件: {ssl_cert_path}")
                except:
                    pass
            
            if ssl_key_path and os.path.exists(ssl_key_path):
                try:
                    os.unlink(ssl_key_path)
                    print(f"[DEBUG] 清理客户端私钥临时文件: {ssl_key_path}")
                except:
                    pass
        
        # 执行后置操作
        if request.post_request_script and not error_message:
 
            if isinstance(request.post_request_script, str):
                operations = [{'type': 'script', 'script': request.post_request_script, 'enabled': True}]
            else:
                operations = request.post_request_script
            
            from .operations import OperationExecutor
            context = await OperationExecutor.execute_operations(
                db=db,
                operations=operations,
                context=context,
                user_id=user_id
            )
            # 更新环境变量
            variables.update(context['env'])
        
        # 执行断言
        assertions_results = []
        if request.assertions and not error_message:
            assertions_results = AssertionEngine.execute_assertions(
                assertions=request.assertions,
                response_data=response_data,
                status_code=status_code,
                response_time=response_time
            )
        
        # 保存执行历史
        from datetime import datetime
        
        # 计算断言是否全部通过
        assertions_passed = None
        if assertions_results:
            assertions_passed = all(r['passed'] for r in assertions_results)
        
        history_data = {
            'request_id': request_id,
            'environment_id': environment_id,
            'environment_name': environment_name,
            'request_data': {
                'method': request.method,
                'url': url,
                'headers': headers,
                'params': params,
                'body': body
            },
            'response_data': response_data,
            'status_code': status_code,
            'response_time': response_time,
            'error_message': error_message or context.get('script_error'),
            'assertions_results': assertions_results,
            'assertions_passed': assertions_passed,
            'executed_by': user_id,
            'executed_at': datetime.now()
        }
        
        history = APIRequestHistoryModel(**history_data)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        
        # 返回执行结果
        return {
            'history_id': history.id,
            'status_code': status_code,
            'response_time': response_time,
            'response_data': response_data,
            'error_message': error_message or context.get('script_error'),
            'assertions_results': assertions_results,
            'assertions_passed': assertions_passed if assertions_passed is not None else True,
            'updated_env': context['env'] if context['env'] != variables else None
        }


# 创建执行器实例
request_executor = RequestExecutor()
