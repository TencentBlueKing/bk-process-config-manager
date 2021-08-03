import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 检查业务下动作权限
    ajaxGetActionsAuth({ rootState }) {
      const params = {
        action_ids: ['view_business', 'operate_config', 'manage_process', 'create_config_template'],
        resources: [{ type: 'biz', id: rootState.bizId }],
      };
      const url = 'api/iam/meta/check_allowed/';
      return http.post(url, params);
    },
    // 权限相关弹框信息
    ajaxGetAuthApplyInfo(context, params = { action_ids: [], resources: [] }) {
      const url = 'api/iam/meta/get_apply_data/';
      return http.post(url, params);
    },
  },
};
