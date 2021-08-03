import http from '@/api';
import queryString from 'query-string';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    example(context, params, config = {}) {
      const mockUrl = `?${AJAX_MOCK_PARAM}=home&invoke=example&${queryString.stringify(params)}`;
      return http.get(mockUrl, params, config);
    },
  },
};
