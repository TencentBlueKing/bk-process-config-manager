import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 指定进程和配置模板查询配置实例
    ajaxGetLatestConfigInstance({ rootState }, { templateId, processId, instId }) {
      let url = `/api/${rootState.bizId}/config_instance/latest_config_instance/?config_template_id=${templateId}&bk_process_id=${processId}`;
      if (instId) {
        url += `&inst_id=${instId}`;
      }
      return http.get(url);
    },
    // 配置生成和下发根据筛选表达式获取实例列表(预览实例列表，下一步进行配置生成)
    ajaxGetConfigInstanceList({ rootState }, { data }) {
      const url = `/api/${rootState.bizId}/config_instance/list_config_instances/`;
      return http.post(url, data);
    },
    // 查询配置实例
    ajaxGetConfigInstanceDetail({ rootState }, { instanceId }) {
      const url = `/api/${rootState.bizId}/config_instance/${instanceId}/`;
      return http.get(url);
    },
  },
};
