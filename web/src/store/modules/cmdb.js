import http from '@/api';

export default {
  namespaced: true,
  state: {
    globalVariables: [],
  },
  mutations: {},
  actions: {
    // 获取全局变量
    async ajaxGetGlobalVariables({ state, rootState }) {
      try {
        const url = `api/${rootState.bizId}/cmdb/biz_global_variables/`;
        const res = await http.get(url);
        state.globalVariables = Object.values(res.data).flat();
      } catch (e) {
        console.warn(e);
      }
    },
    // 获取业务列表
    ajaxGetBizList() {
      const url = 'api/0/cmdb/biz_list/';
      return http.get(url);
    },

    // 根据业务查询拓扑
    ajaxGetBizTopo({ rootState }) {
      const url = `api/${rootState.bizId}/cmdb/biz_topo/`;
      return http.get(url);
    },
    // 根据业务查询服务模板列表
    ajaxGetServiceTemplate({ rootState }) {
      const url = `api/${rootState.bizId}/cmdb/service_template/`;
      return http.get(url);
    },

    // 根据业务获取集群列表
    ajaxGetSetListByEnv({ rootState }, { setEnv }) {
      const url = `api/${rootState.bizId}/cmdb/set_list/?bk_set_env=${setEnv}`;
      return http.get(url);
    },
    // 根据集群获取模块列表
    ajaxGetModuleListBySet({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/cmdb/module_list/`;
      return http.post(url, data);
    },
    // 根据模块获取服务实例列表
    ajaxGetServiceListByModule({ rootState }, { withProcCount, data }) {
      let url = `api/${rootState.bizId}/cmdb/service_instance/`;
      if (withProcCount) {
        url += '?with_proc_count=true';
      }
      return http.post(url, data);
    },
    // 查询对象模型属性
    ajaxGetProcessInstanceList({ rootState }) {
      const url = `/api/${rootState.bizId}/cmdb/search_object_attribute/?bk_obj_id=process`;
      return http.get(url);
    },
    // 查询进程实例的相关信息
    ajaxGetProcessRelated({ rootState }, params) {
      const url = `/api/${rootState.bizId}/cmdb/list_process_related_info/`;
      return http.post(url, params);
    },
    // 查询进程实例的相关信息
    ajaxGetCheckServiceTemplate({ rootState }, params) {
      const url = `/api/${rootState.bizId}/cmdb/check_service_template_difference/`;
      return http.get(url, { params });
    },
    // 查询进程实例的相关信息
    ajaxGetBatchCheckServiceTemplate({ rootState }) {
      const url = `/api/${rootState.bizId}/cmdb/batch_check_service_template_difference/`;
      return http.get(url);
    },
  },
};
