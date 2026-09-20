import { ref } from '@vue/composition-api';

/**
 * 轮询
 * @param cb 回调
 * @param interval 轮询周期
 * @param immediate 立即执行
 */
export default function useIntervalFn(
  cb,
  interval = 5000,
  immediate = false,
) {
  const isPending = ref(false);
  const flag = ref(false);

  const timer = ref(null);

  function clear() {
    if (timer.value) {
      clearTimeout(timer.value);
      timer.value = null;
    }
  }

  function stop() {
    isPending.value = false;
    flag.value = false;
    clear();
  }

  function start(...args) {
    clear();
    if (!interval) return;

    flag.value = true;
    async function timerFn() {
      // 上一个接口未执行完，不执行本次轮询
      if (isPending.value) return;

      isPending.value = true;
      await cb(...args);
      isPending.value = false;
      if (flag.value) {
        timer.value = setTimeout(timerFn, interval);
      }
    }
    setTimeout(() => timerFn(), immediate ? 0 : interval);
  }

  return {
    isPending,
    timer,
    start,
    stop,
  };
}
