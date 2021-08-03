import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 指定进程预览配置版本
    ajaxPreviewConfigVersion({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/config_version/preview/`;
      return http.post(url, data);
    },
    // 获取配置版本详情
    ajaxGetConfigVersionDetail({ rootState }, { versionId }) {
      const url = `api/${rootState.bizId}/config_version/${versionId}/`;
      return http.get(url);
    },
    // 编辑配置模板版本（草稿暂存、覆盖）
    ajaxUpdateConfigVersion({ rootState }, { versionId, data }) {
      const url = `api/${rootState.bizId}/config_version/${versionId}/`;
      return http.put(url, data);
    },
    // 新建配置模板版本（根据指定版本克隆）
    ajaxCreateConfigVersion({ rootState }, { versionId, data }) {
      const url = `api/${rootState.bizId}/config_version/${versionId}/clone/`;
      return http.post(url, data);
    },
  },
};
