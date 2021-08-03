import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 刷新业务进程缓存
    ajaxFlushProcess({ rootState }) {
      const url = `api/${rootState.bizId}/process/flush_process/`;
      return http.post(url);
    },
    // 同步进程状态
    ajaxSynchProcessStatus({ rootState }) {
      const url = `api/${rootState.bizId}/process/sync_process_status/`;
      return http.post(url);
    },
    // 进程操作
    ajaxSetOperateProcess({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/process/operate_process/`;
      return http.post(url, data);
    },
    // 进程状态列表
    ajaxGetProcessStatusList({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/process/process_status/`;
      return http.post(url, data);
    },
    // 跟新进程实例
    ajaxUpdateProcessInstance({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/process/update_process_instance/`;
      return http.post(url, data);
    },
    // 跟新进程模板
    ajaxUpdateProcessTemplate({ rootState }, { data }) {
      const url = `api/${rootState.bizId}/process/update_process_template/`;
      return http.post(url, data);
    },
    // 根据服务实例获取进程实例列表概要信息
    ajaxGetProcessListByService({ rootState }, params) {
      const url = `api/${rootState.bizId}/process/process_instance_simple/`;
      return http.post(url, params.data);
    },
    // 根据服务实例查询实例进程列表
    ajaxGetInstanceProcessByServiceInstance({ rootState }, params) {
      const url = `api/${rootState.bizId}/process/process_instance/?service_instance_id=${params.serviceInstanceId}`;
      return http.get(url);
    },
    // 根据服务模板查询模板进程列表
    ajaxGetTemplateProcessByServiceTemplate({ rootState }, params) {
      const url = `api/${rootState.bizId}/process/process_template/?service_template_id=${params.serviceTemplateId}`;
      return http.get(url);
    },
    // 创建进程实例
    ajaxCreateProcessInstance({ rootState }, params) {
      const url = `api/${rootState.bizId}/process/create_process_instance/`;
      return http.post(url, params.data);
    },
    // 创建进程模板
    ajaxCreateProcessTemplate({ rootState }, params) {
      const url = `api/${rootState.bizId}/process/create_process_template/`;
      return http.post(url, params.data);
    },
    // 创建进程模板
    ajaxDeleteProcessInstance({ rootState }, params) {
      const url = `/api/${rootState.bizId}/process/delete_process_instance/`;
      return http.post(url, params.data);
    },
    // 创建进程模板
    ajaxDeleteProcessTemplate({ rootState }, params) {
      const url = `api/${rootState.bizId}/process/delete_process_template/`;
      return http.post(url, params.data);
    },
  },
};
