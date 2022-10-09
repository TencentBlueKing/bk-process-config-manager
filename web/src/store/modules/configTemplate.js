import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 获取配置模板列表 page, pagesize, search, ordering
    ajaxGetConfigTemplateList({ rootState }, query = {}) {
      let url = `api/${rootState.bizId}/config_template/`;
      const queryArr = [];
      Object.keys(query).reduce((arr, key) => {
        if (query[key]) {
          arr.push(`${key}=${query[key]}`);
        }
        return arr;
      }, queryArr);
      if (queryArr.length) {
        url += `?${queryArr.join('&')}`;
      }
      return http.get(url);
    },
    // 新建配置模板
    ajaxCreateConfigTemplate({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/config_template/`;
      return http.post(url, data);
    },
    // 获取配置模板详情
    ajaxGetConfigTemplateDetail({ rootState }, { templateId }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/`;
      return http.get(url);
    },
    // 更新配置模板
    ajaxUpdateConfigTemplate({ rootState }, { templateId, data }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/`;
      return http.patch(url, data);
    },
    // 删除配置模板
    ajaxDeleteConfigTemplate({ rootState }, { templateId }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/`;
      return http.delete(url);
    },

    // 配置模板绑定到进程
    ajaxBindTemplateToProcess({ rootState }, { templateId, data }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/bind_template_to_process/`;
      return http.post(url, data);
    },

    // 绑定进程到配置模板
    ajaxBindProcessToTemplate({ rootState }, { data }) {
      const url = `/api/${rootState.bizId}/config_template/bind_process_to_template/`;
      return http.post(url, data);
    },

    // 绑定关系回填
    ajaxGetTemplateBindRelationship({ rootState }, { templateId }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/list_binding_relationship/`;
      return http.get(url);
    },

    // 配置生成
    ajaxGenerateConfig({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/config_template/generate_config/`;
      return http.post(url, data);
    },

    // 获取配置文件版本列表
    ajaxGetConfigVersionList({ rootState }, { templateId }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/list_version/`;
      return http.get(url);
    },

    // 进程配置下发
    ajaxSetReleaseConfig({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/config_template/release_config/`;
      return http.post(url, data);
    },
    // 配置文件检查
    ajaxSetDiffConfig({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/config_template/diff_config/`;
      return http.post(url, data);
    },

    // 同步配置生成
    ajaxSyncGenerateConfig({ rootState }, { templateId, data }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/sync_generate_config/`;
      return http.post(url, data, {
        cancelPrevious: false,
      });
    },

    // 新建全新草稿
    ajaxCreateNewConfigVersion({ rootState }, { templateId, data }) {
      const url = `api/${rootState.bizId}/config_template/${templateId}/create_config_version/`;
      return http.post(url, data);
    },

    // 获取模板列表(选中置顶)
    ajaxGetNewConfigTemplateList({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/config_template/config_templates_list/`;
      return http.post(url, data);
    },
  },
};
