import request from '/@/utils/request';

/**
 * AI 知识库配置 API
 */
export function useAiKnowledgeConfigApi() {
  return {
    getGlobal: () =>
      request({ 
        url: '/v1/ai/knowledge-config/global', 
        method: 'GET' 
      }),
    saveGlobal: (data: any) =>
      request({ 
        url: '/v1/ai/knowledge-config/global', 
        method: 'PUT', 
        data 
      }),
    testEmbedding: (data: any) =>
      request({ 
        url: '/v1/ai/knowledge-config/test-embedding', 
        method: 'POST', 
        data 
      }),
    testVectorDb: (data: any) =>
      request({ 
        url: '/v1/ai/knowledge-config/test-vector-db', 
        method: 'POST', 
        data 
      }),
  };
}

export const aiKnowledgeConfigApi = useAiKnowledgeConfigApi();
