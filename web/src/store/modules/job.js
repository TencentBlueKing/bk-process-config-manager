import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 任务列表
    ajaxGetJobList({ rootState }, { page, pagesize, query, ordering }) {
      let url = `api/${rootState.bizId}/job/?page=${page}&pagesize=${pagesize}`;
      if (!page) {
        url = `api/${rootState.bizId}/job/?pagesize=${pagesize}`;
      }
      if (query) {
        for (const [key, val] of Object.entries(query)) {
          let queryName = key;
          let description = val;
          if (Array.isArray(val)) {
            queryName = val.length > 1 ? `${key}__in` : key;
            description = val.join(',');
          }
          url += `&${queryName}=${description}`;
        }
      }
      if (ordering) {
        url += `&ordering=${ordering}`;
      }
      return http.get(url);
    },
    // 任务详情
    ajaxGetJobDetail({ rootState }, { jobId }) {
      const url = `api/${rootState.bizId}/job/${jobId}/`;
      return http.get(url);
    },
    // 任务状态查询
    ajaxGetJobStatus({ rootState }, { jobId, data }) {
      const url = `api/${rootState.bizId}/job/${jobId}/job_status/`;
      return http.post(url, data);
    },
    // 任务详情列表
    ajaxGetJobTaskList({ rootState }, { jobId, data }) {
      const url = `api/${rootState.bizId}/job/${jobId}/job_task/`;
      return http.post(url, data);
    },
    // 任务详情统计（按错误码）
    ajaxGetJobTaskStatistics({ rootState }, { jobId }) {
      const url = `api/${rootState.bizId}/job/${jobId}/job_task_statistics/`;
      return http.get(url);
    },
    // 重试
    ajaxRetryJob({ rootState }, { jobId, data }) {
      const url = `api/${rootState.bizId}/job/${jobId}/retry/`;
      return http.post(url, data);
    },
    // 查询任务IP
    ajaxGetSearchIp({ rootState }, { jobId, status }) {
      const url = `api/${rootState.bizId}/job/${jobId}/search_ip/?status=${status}`;
      return http.get(url);
    },
  },
};
