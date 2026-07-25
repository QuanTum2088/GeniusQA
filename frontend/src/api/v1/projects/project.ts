import request from '/@/utils/request';

/**
 * 项目管理API
 */
export function useProjectApi() {
  return {
   
    
    // 获取项目列表
    getList: (params?: {
      page?: number;
      page_size?: number;
      name?: string;
      status?: string;
    }) => {
      return request({
        url: '/v1/Ntesterc_project/',
        method: 'GET',
        params,
      });
    },
    
    // 获取项目详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/Ntesterc_project/${id}`,
        method: 'GET',
      });
    },
    
    // 创建项目
    create: (data: {
      name: string;
      description?: string;
      status?: string;
    }) => {
      return request({
        url: '/v1/Ntesterc_project/',
        method: 'POST',
        data,
      });
    },
    
    // 更新项目
    update: (id: number, data: {
      name?: string;
      description?: string;
      status?: string;
    }) => {
      return request({
        url: `/v1/Ntesterc_project/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除项目
    delete: (id: number) => {
      return request({
        url: `/v1/Ntesterc_project/${id}`,
        method: 'DELETE',
      });
    },
    

    
    // 获取项目成员列表
    getMemberList: (projectId: number) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/members`,
        method: 'GET',
      });
    },
    
    // 添加项目成员
    addMember: (projectId: number, data: {
      user_id: number;
      role: string;
    }) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/members`,
        method: 'POST',
        data,
      });
    },
    
    // 更新成员角色
    updateMemberRole: (projectId: number, memberId: number, data: {
      role: string;
    }) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/members/${memberId}`,
        method: 'PUT',
        data,
      });
    },
    
    // 移除项目成员
    removeMember: (projectId: number, memberId: number) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/members/${memberId}`,
        method: 'DELETE',
      });
    },
    
 
    
    // 获取项目环境列表
    getEnvironmentList: (projectId: number) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/environments`,
        method: 'GET',
      });
    },
    
    // 创建项目环境
    createEnvironment: (projectId: number, data: {
      name: string;
      base_url?: string;
      description?: string;
      variables?: Record<string, any>;
      is_default?: boolean;
    }) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/environments`,
        method: 'POST',
        data,
      });
    },
    
    // 更新项目环境
    updateEnvironment: (projectId: number, envId: number, data: {
      name?: string;
      base_url?: string;
      description?: string;
      variables?: Record<string, any>;
      is_default?: boolean;
    }) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/environments/${envId}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除项目环境
    deleteEnvironment: (projectId: number, envId: number) => {
      return request({
        url: `/v1/Ntesterc_project/${projectId}/environments/${envId}`,
        method: 'DELETE',
      });
    },
  };
}

export const getProjectList = (params?: {
  page?: number;
  page_size?: number;
  name?: string;
  status?: string;
}) => useProjectApi().getList(params);

export const getProjectDetail = (id: number) => useProjectApi().getDetail(id);

export const createProject = (data: {
  name: string;
  description?: string;
  status?: string;
}) => useProjectApi().create(data);

export const updateProject = (
  id: number,
  data: {
    name?: string;
    description?: string;
    status?: string;
  }
) => useProjectApi().update(id, data);

export const deleteProject = (id: number) => useProjectApi().delete(id);
