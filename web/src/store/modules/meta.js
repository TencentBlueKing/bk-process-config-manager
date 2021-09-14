import http from '@/api';

export default {
  namespaced: true,
  state: {
    footerContent: null,
  },
  mutations: {},
  actions: {
    ajaxGetUserInfo() {
      const url = 'api/0/meta/get_user_info/';
      return http.get(url);
    },
    async ajaxGetFooter({ state }) {
      try {
        const url = 'api/0/meta/footer/';
        const res = await http.get(url);
        state.footerContent = res.data;
      } catch (e) {
        console.warn(e);
      }
    },
    // 任务历史过滤选项
    ajaxGetHistoryFilterList({ rootState }) {
      const url = `api/${rootState.bizId}/meta/job_filter_choices/`;
      return http.get(url);
    },
    // 任务详细过滤选项
    ajaxGetTaskFilterCondition({ rootState }, { jobId }) {
      const url = `/api/${rootState.bizId}/meta/job_task_filter_choices/?job_id=${jobId}`;
      return http.get(url);
    },
    // 进程状态过滤选项
    ajaxGetStatusFilterCondition({ rootState }) {
      const url = `/api/${rootState.bizId}/meta/process_filter_choices/`;
      return http.get(url);
    },
    // 记录用户访问记录
    ajaxGetUserVisit({ rootState }) {
      return http.post('/meta/visit/', { bk_biz_id: rootState.bizId });
    },
    ajaxFrequencyStatistics(context, params) {
      return http.post('/meta/frequency_statistics/', params);
    },
    ajaxTrendStatistics(context, params) {
      return http.post('/meta/trend_statistics/', params);
    },
    ajaxJobCountStatistics(context, params) {
      return http.post('/meta/job_count_statistics_with_orm/', params);
    },
  },
};
