export default {
  work_path: [
    {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    },
  ],
  user: [
    {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    },
  ],
  pid_file: [
    {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    },
  ],
  start_cmd: [
    {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    },
  ],
  stop_cmd: [
    {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    },
  ],
  bk_process_name: [
    {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    },
  ],
  bk_func_name: [
    {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    },
  ],
  timeout: [{
    validator(val) {
      if (!val || val === '0' || /-/.test(val)) {
        return true;
      }
    },
    message: window.i18n.t('请输入正整数'),
    trigger: 'blur',
  }],
  bk_start_check_secs: [{
    validator(val) {
      if (!val || val === '0' || /-/.test(val)) {
        return true;
      }
    },
    message: window.i18n.t('请输入正整数'),
    trigger: 'blur',
  }],
  priority: [{
    validator(val) {
      if (!/^-?\d+$/.test(val)) {
        return true;
      }
    },
    required: true,
    message: window.i18n.t('请输入整数'),
    trigger: 'blur',
  }],
  proc_num: [{
    validator(val) {
      console.log(/-/.test(val), val);
      if (!val || val === '0' || /-/.test(val)) {
        return true;
      }
    },
    message: window.i18n.t('请输入正整数'),
    trigger: 'blur',
  }],
};
