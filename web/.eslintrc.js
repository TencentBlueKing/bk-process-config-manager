/**
 * @file eslint config
 * @author blueking
 */

module.exports = {
  root: true,
  extends: ['@bkui/eslint-config-bk/vue'],
  globals: {
    // value 为 true 允许被重写，为 false 不允许被重写
    NODE_ENV: false,
    LOCAL_DEV_URL: false,
    LOCAL_DEV_PORT: false,
    AJAX_MOCK_PARAM: false,
  },
  // add your custom rules hered
  rules: {
    'no-param-reassign': 'off',
  },
};
