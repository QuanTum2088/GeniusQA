#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
import asyncio
import time
import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession


class OperationType:
    """操作类型常量"""
    SCRIPT = 'script'  # 自定义脚本
    PUBLIC_SCRIPT = 'public_script'  # 公共脚本
    DATABASE = 'database'  # 数据库操作
    WAIT = 'wait'  # 等待时间
    EXTRACT = 'extract'  # 提取变量
    IMPORT_REQUEST = 'import_request'  # 从其它接口导入
    ASSERTION = 'assertion'  # 断言（仅后置）


class ScriptOperationExecutor:
    """脚本操作执行器"""
    
    @staticmethod
    def execute(
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行自定义脚本"""
        script = operation.get('script', '')
        if not script or not script.strip():
            return context
        
        # 创建受限的执行环境
        # 注意：env需要是一个新的字典，这样修改才能被捕获
        env_dict = context.get('env', {}).copy()
        
        safe_globals = {
            '__builtins__': {
                '__import__': __import__,  # 允许导入模块
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
                'time': __import__('time'),  # 预导入常用模块
                'hashlib': __import__('hashlib'),
            },
            'context': context,
            'env': env_dict,
            'request': context.get('request', {}),
            'response': context.get('response', {}),
        }
        
        try:
            # 执行脚本
            exec(script, safe_globals)
            
            # 更新上下文 - 从safe_globals中获取修改后的env
            context['env'] = safe_globals['env']
            
            return context
        
        except Exception as e:
            context['script_error'] = str(e)
            return context


class PublicScriptOperationExecutor:
    """公共脚本操作执行器"""
    
    @staticmethod
    async def execute(
        db: AsyncSession,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行公共脚本"""
        script_id = operation.get('script_id')
        if not script_id:
            context['script_error'] = '未指定公共脚本ID'
            return context
        
        # 获取公共脚本
        from .crud import PublicScriptCRUD
        crud = PublicScriptCRUD(db)
        script = await crud.get_by_id_crud(script_id)
        
        if not script or not script.is_active:
            context['script_error'] = f'公共脚本不存在或已禁用: {script_id}'
            return context
        
        # 执行脚本
        return ScriptOperationExecutor.execute(
            {'script': script.script_content},
            context
        )


class DatabaseOperationExecutor:
    """数据库操作执行器"""
    
    @staticmethod
    async def execute(
        db: AsyncSession,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行数据库操作"""
        db_config_id = operation.get('db_config_id')
        sql = operation.get('sql', '')
        save_to_var = operation.get('save_to_var')  # 保存结果到变量
        
        if not db_config_id or not sql:
            context['db_error'] = '数据库配置ID或SQL语句为空'
            return context
        
        try:
            # 获取数据库配置
            from .crud import DatabaseConfigCRUD
            crud = DatabaseConfigCRUD(db)
            db_config = await crud.get_by_id_crud(db_config_id)
            
            if not db_config or not db_config.is_active:
                context['db_error'] = f'数据库配置不存在或已禁用: {db_config_id}'
                return context
            
            # 根据数据库类型执行SQL
            if db_config.db_type == 'mysql':
                result = await DatabaseOperationExecutor._execute_mysql(db_config, sql, context)
            elif db_config.db_type == 'postgresql':
                result = await DatabaseOperationExecutor._execute_postgresql(db_config, sql, context)
            elif db_config.db_type == 'mongodb':
                result = await DatabaseOperationExecutor._execute_mongodb(db_config, sql, context)
            elif db_config.db_type == 'redis':
                result = await DatabaseOperationExecutor._execute_redis(db_config, sql, context)
            else:
                context['db_error'] = f'不支持的数据库类型: {db_config.db_type}'
                return context
            
            # 保存结果到变量
            if save_to_var and result is not None:
                context['env'][save_to_var] = result
            
            return context
        
        except Exception as e:
            context['db_error'] = str(e)
            return context
    
    @staticmethod
    async def _execute_mysql(db_config, sql: str, context: Dict[str, Any]):
        """执行MySQL查询"""
        import asyncmy
        
        # 解析变量
        from .executor import VariableResolver
        sql = VariableResolver.resolve_variables(sql, context.get('env', {}))
        
        connection = await asyncmy.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.username,
            password=db_config.password,
            db=db_config.database_name,
        )
        
        try:
            async with connection.cursor(asyncmy.DictCursor) as cursor:
                await cursor.execute(sql)
                
                # 判断是查询还是修改
                if sql.strip().upper().startswith('SELECT'):
                    result = await cursor.fetchall()
                    return result
                else:
                    await connection.commit()
                    return {'affected_rows': cursor.rowcount}
        finally:
            connection.close()
    
    @staticmethod
    async def _execute_postgresql(db_config, sql: str, context: Dict[str, Any]):
        """执行PostgreSQL查询"""
        # TODO: 实现PostgreSQL支持
        raise NotImplementedError('PostgreSQL支持待实现')
    
    @staticmethod
    async def _execute_mongodb(db_config, sql: str, context: Dict[str, Any]):
        """执行MongoDB查询"""
        # TODO: 实现MongoDB支持
        raise NotImplementedError('MongoDB支持待实现')
    
    @staticmethod
    async def _execute_redis(db_config, sql: str, context: Dict[str, Any]):
        """执行Redis命令"""
        # TODO: 实现Redis支持
        raise NotImplementedError('Redis支持待实现')


class WaitOperationExecutor:
    """等待操作执行器"""
    
    @staticmethod
    async def execute(
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行等待操作"""
        wait_time = operation.get('wait_time', 0)  # 毫秒
        
        if wait_time > 0:
            await asyncio.sleep(wait_time / 1000)  # 转换为秒
        
        return context


class ExtractOperationExecutor:
    """提取变量操作执行器"""
    
    @staticmethod
    def execute(
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取变量"""
        extract_type = operation.get('extract_type')  # jsonpath/regex/header
        source = operation.get('source', 'body')  # body/header/status
        expression = operation.get('expression')
        var_name = operation.get('var_name')
        
        if not expression or not var_name:
            return context
        
        try:
            response = context.get('response', {})
            
            if extract_type == 'jsonpath':
                # JSONPath提取
                from jsonpath_ng import parse as jsonpath_parse
                
                if source == 'body':
                    data = response.get('body', {})
                elif source == 'header':
                    data = response.get('headers', {})
                else:
                    data = response
                
                jsonpath_expr = jsonpath_parse(expression)
                matches = jsonpath_expr.find(data)
                
                if matches:
                    context['env'][var_name] = matches[0].value
            
            elif extract_type == 'regex':
                # 正则表达式提取
                if source == 'body':
                    text = json.dumps(response.get('body', {}))
                elif source == 'header':
                    text = json.dumps(response.get('headers', {}))
                else:
                    text = json.dumps(response)
                
                match = re.search(expression, text)
                if match:
                    context['env'][var_name] = match.group(1) if match.groups() else match.group(0)
            
            elif extract_type == 'header':
                # 直接从响应头提取
                headers = response.get('headers', {})
                if expression in headers:
                    context['env'][var_name] = headers[expression]
            
            return context
        
        except Exception as e:
            context['extract_error'] = str(e)
            return context


class ImportRequestOperationExecutor:
    """导入其它接口操作执行器"""
    
    @staticmethod
    async def execute(
        db: AsyncSession,
        operation: Dict[str, Any],
        context: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """执行其它接口并导入结果"""
        request_id = operation.get('request_id')
        environment_id = operation.get('environment_id')
        
        if not request_id:
            context['import_error'] = '未指定要导入的接口ID'
            return context
        
        try:
            # 执行其它接口
            from .executor import RequestExecutor
            result = await RequestExecutor.execute_request(
                db=db,
                request_id=request_id,
                environment_id=environment_id,
                user_id=user_id
            )
            
            # 将结果合并到当前上下文
            if result.get('updated_env'):
                context['env'].update(result['updated_env'])
            
            # 保存响应数据
            context['imported_response'] = result.get('response_data', {})
            
            return context
        
        except Exception as e:
            context['import_error'] = str(e)
            return context


class OperationExecutor:
    """操作执行器 - 统一入口"""
    
    @staticmethod
    async def execute_operations(
        db: AsyncSession,
        operations: List[Dict[str, Any]],
        context: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """执行操作列表"""
        if not operations:
            return context
        
        for operation in operations:
            operation_type = operation.get('type')
            enabled = operation.get('enabled', True)
            
            if not enabled:
                continue
            
            try:
                if operation_type == OperationType.SCRIPT:
                    context = ScriptOperationExecutor.execute(operation, context)
                
                elif operation_type == OperationType.PUBLIC_SCRIPT:
                    context = await PublicScriptOperationExecutor.execute(db, operation, context)
                
                elif operation_type == OperationType.DATABASE:
                    context = await DatabaseOperationExecutor.execute(db, operation, context)
                
                elif operation_type == OperationType.WAIT:
                    context = await WaitOperationExecutor.execute(operation, context)
                
                elif operation_type == OperationType.EXTRACT:
                    context = ExtractOperationExecutor.execute(operation, context)
                
                elif operation_type == OperationType.IMPORT_REQUEST:
                    context = await ImportRequestOperationExecutor.execute(db, operation, context, user_id)
                
                # 如果有错误，记录但继续执行
                if any(key.endswith('_error') for key in context.keys()):
                    print(f"[WARNING] 操作执行出错: {operation_type}")
            
            except Exception as e:
                print(f"[ERROR] 操作执行异常: {operation_type} - {str(e)}")
                context[f'{operation_type}_error'] = str(e)
        
        return context
