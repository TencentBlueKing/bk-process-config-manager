/**
 * @file 通用方法
 * @author blueking
 */

/**
 * 函数柯里化
 *
 * @example
 *     function add (a, b) {return a + b}
 *     curry(add)(1)(2)
 *
 * @param {Function} fn 要柯里化的函数
 *
 * @return {Function} 柯里化后的函数
 */
export function curry(fn) {
  const judge = (...args) => (args.length === fn.length
    ? fn(...args)
    : arg => judge(...args, arg));
  return judge;
}

/**
 * 判断是否是对象
 *
 * @param {Object} obj 待判断的
 *
 * @return {boolean} 判断结果
 */
export function isObject(obj) {
  return obj !== null && typeof obj === 'object';
}

/**
 * 返回指定闭区间数值
 * @param {Number} value
 * @param {Number} min
 * @param {Number} max
 * @returns {Number}
 */
export function clamp(value, min, max) {
  if (value < min) {
    return min;
  }

  if (value > max) {
    return max;
  }

  return value;
}

/**
 * 规范化参数
 *
 * @param {Object|string} type vuex type
 * @param {Object} payload vuex payload
 * @param {Object} options vuex options
 *
 * @return {Object} 规范化后的参数
 */
export function unifyObjectStyle(type, payload, options) {
  if (isObject(type) && type.type) {
    options = payload;
    payload = type;
    type = type.type;
  }

  if (NODE_ENV !== 'production') {
    if (typeof type !== 'string') {
      console.warn(`expects string as the type, but found ${typeof type}.`);
    }
  }

  return { type, payload, options };
}

/**
 * 以 baseColor 为基础生成随机颜色
 *
 * @param {string} baseColor 基础颜色
 * @param {number} count 随机颜色个数
 *
 * @return {Array} 颜色数组
 */
export function randomColor(baseColor, count) {
  const segments = baseColor.match(/[\da-z]{2}/g);
  // 转换成 rgb 数字
  for (let i = 0; i < segments.length; i++) {
    segments[i] = parseInt(segments[i], 16);
  }
  const ret = [];
  // 生成 count 组颜色，色差 20 * Math.random
  for (let i = 0; i < count; i++) {
    ret[i] = `#${
      Math.floor(segments[0] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
    }${Math.floor(segments[1] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
    }${Math.floor(segments[2] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)}`;
  }
  return ret;
}

/**
 * min max 之间的随机整数
 *
 * @param {number} min 最小值
 * @param {number} max 最大值
 *
 * @return {number} 随机数
 */
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

/**
 * 异常处理
 *
 * @param {Object} err 错误对象
 * @param {Object} ctx 上下文对象，这里主要指当前的 Vue 组件
 */
export function catchErrorHandler(err, ctx) {
  const { data } = err;
  if (data) {
    if (!data.code || data.code === 404) {
      ctx.exceptionCode = {
        code: '404',
        msg: '当前访问的页面不存在',
      };
    } else if (data.code === 403) {
      ctx.exceptionCode = {
        code: '403',
        msg: 'Sorry，您的权限不足!',
      };
    } else {
      console.error(err);
      ctx.bkMessageInstance = ctx.$bkMessage({
        theme: 'error',
        message: err.message || err.data.msg || err.statusText,
      });
    }
  } else {
    console.error(err);
    ctx.bkMessageInstance = ctx.$bkMessage({
      theme: 'error',
      message: err.message || err.data.msg || err.statusText,
    });
  }
}

/**
 * 获取字符串长度，中文算两个，英文算一个
 *
 * @param {string} str 字符串
 *
 * @return {number} 结果
 */
export function getStringLen(str) {
  let len = 0;
  for (let i = 0; i < str.length; i++) {
    if (str.charCodeAt(i) > 127 || str.charCodeAt(i) === 94) {
      len += 2;
    } else {
      len += 1;
    }
  }
  return len;
}

/**
 * 对象转为 url query 字符串
 *
 * @param {*} param 要转的参数
 * @param {string} key key
 *
 * @return {string} url query 字符串
 */
export function json2Query(param, key) {
  const mappingOperator = '=';
  const separator = '&';
  let paramStr = '';

  if (param instanceof String || typeof param === 'string'
            || param instanceof Number || typeof param === 'number'
            || param instanceof Boolean || typeof param === 'boolean'
  ) {
    paramStr += separator + key + mappingOperator + encodeURIComponent(param);
  } else {
    Object.keys(param).forEach((p) => {
      const value = param[p];
      const k = (key === null || key === '' || key === undefined)
        ? p
        : key + (param instanceof Array ? `[${p}]` : `.${p}`);
      paramStr += separator + json2Query(value, k);
    });
  }
  return paramStr.substr(1);
}

/**
 * 字符串转换为驼峰写法
 *
 * @param {string} str 待转换字符串
 *
 * @return {string} 转换后字符串
 */
export function camelize(str) {
  return str.replace(/-(\w)/g, (strMatch, p1) => p1.toUpperCase());
}

/**
 * 获取元素的样式
 *
 * @param {Object} elem dom 元素
 * @param {string} prop 样式属性
 *
 * @return {string} 样式值
 */
export function getStyle(elem, prop) {
  if (!elem || !prop) {
    return false;
  }

  // 先获取是否有内联样式
  let value = elem.style[camelize(prop)];

  if (!value) {
    // 获取的所有计算样式
    let css = '';
    if (document.defaultView && document.defaultView.getComputedStyle) {
      css = document.defaultView.getComputedStyle(elem, null);
      value = css ? css.getPropertyValue(prop) : null;
    }
  }

  return String(value);
}

/**
 *  获取元素相对于页面的高度
 *
 *  @param {Object} node 指定的 DOM 元素
 */
export function getActualTop(node) {
  let actualTop = node.offsetTop;
  let current = node.offsetParent;

  while (current !== null) {
    actualTop += current.offsetTop;
    current = current.offsetParent;
  }

  return actualTop;
}

/**
 *  获取元素相对于页面左侧的宽度
 *
 *  @param {Object} node 指定的 DOM 元素
 */
export function getActualLeft(node) {
  let actualLeft = node.offsetLeft;
  let current = node.offsetParent;

  while (current !== null) {
    actualLeft += current.offsetLeft;
    current = current.offsetParent;
  }

  return actualLeft;
}

/**
 * document 总高度
 *
 * @return {number} 总高度
 */
export function getScrollHeight() {
  let scrollHeight = 0;
  let bodyScrollHeight = 0;
  let documentScrollHeight = 0;

  if (document.body) {
    bodyScrollHeight = document.body.scrollHeight;
  }

  if (document.documentElement) {
    documentScrollHeight = document.documentElement.scrollHeight;
  }

  scrollHeight = (bodyScrollHeight - documentScrollHeight > 0) ? bodyScrollHeight : documentScrollHeight;

  return scrollHeight;
}

/**
 * 滚动条在 y 轴上的滚动距离
 *
 * @return {number} y 轴上的滚动距离
 */
export function getScrollTop() {
  let scrollTop = 0;
  let bodyScrollTop = 0;
  let documentScrollTop = 0;

  if (document.body) {
    bodyScrollTop = document.body.scrollTop;
  }

  if (document.documentElement) {
    documentScrollTop = document.documentElement.scrollTop;
  }

  scrollTop = (bodyScrollTop - documentScrollTop > 0) ? bodyScrollTop : documentScrollTop;

  return scrollTop;
}

/**
 * 浏览器视口的高度
 *
 * @return {number} 浏览器视口的高度
 */
export function getWindowHeight() {
  const windowHeight = document.compatMode === 'CSS1Compat'
    ? document.documentElement.clientHeight
    : document.body.clientHeight;

  return windowHeight;
}

/**
 * 简单的 loadScript
 *
 * @param {string} url js 地址
 * @param {Function} callback 回调函数
 */
export function loadScript(url, callback) {
  const script = document.createElement('script');
  script.async = true;
  script.src = url;

  script.onerror = () => {
    callback(new Error(`Failed to load: ${url}`));
  };

  script.onload = () => {
    callback();
  };

  document.getElementsByTagName('head')[0].appendChild(script);
}

/**
 * 服务模板名称排序，中文按拼音排，其它按编码顺序排
 * @param {String} prop 排序的数组对象属性
 */
export function sortByCustom(prop) {
  const reg = /^[\u4E00-\u9FA5]+$/;
  return function (obj1, obj2) {
    try {
      const value1 = obj1[prop].toUpperCase();
      const value2 = obj2[prop].toUpperCase();
      if (reg.test(value1[0]) && reg.test(value2[0])) {
        return value1.localeCompare(value2, 'zh-CN');
      }
      if (value1 < value2) {
        return -1;
      } if (value1 > value2) {
        return 1;
      }
      return 0;
    } catch (error) {
      console.warn(error);
      return 0;
    }
  };
}

/**
 * 表格按ASCII字符顺序排序
 * @param {String} property 排序的表格行属性
 */
export function sortByASCII(property) {
  return function (a, b) {
    try {
      const x = a[property].toUpperCase();
      const y = b[property].toUpperCase();
      if (x < y) {
        return -1;
      } if (x > y) {
        return 1;
      }
      return 0;
    } catch (e) {
      console.warn(e);
      return 0;
    }
  };
}
/**
 * 表格按时间顺序排序
 * @param {String} property 排序的表格行属性
 */
export function sortByDate(property) {
  return function (a, b) {
    try {
      const x = Date.parse(a[property]);
      const y = Date.parse(b[property]);
      return x - y;
    } catch (e) {
      console.warn(e);
      return 0;
    }
  };
}
/**
 * 表格按数字大小排序
 * @param {String} property 排序的表格行属性
 */
export function sortByNumber(property) {
  return function (a, b) {
    try {
      const x = Number(a[property]);
      const y = Number(b[property]);
      return x - y;
    } catch (e) {
      console.warn(e);
      return 0;
    }
  };
}
/**
 * 表格按数字大小排序
 * @param {String} property 排序的表格行属性
 */
export function sortByPercent(property) {
  return function (a, b) {
    try {
      const x = Number(a[property].slice(0, -1));
      const y = Number(b[property].slice(0, -1));
      return x - y;
    } catch (e) {
      console.warn(e);
      return 0;
    }
  };
}
/**
 * 表格筛选
 * @param {String} value 筛选的值
 * @param {Object} row 表格行原始数据
 * @param {Object} column 表格行数据
 * @param {String} column.property 表格行过滤属性
 */
export function commonFilterMethod(value, row, column) {
  const { property } = column;
  return row[property] === value;
}

/**
 *  * 执行耗时
 * @param {Number} startTime 开始时间
 * @param {Number} endTime 结束时间
 * @return {String}
 */
export function performTime(startTime, endTime) {
  const startTimeStamp = Date.parse(new Date(startTime));
  const endTimeStamp = Date.parse(new Date(endTime));
  if (!startTimeStamp || !endTimeStamp) return;
  let timeout = endTimeStamp - startTimeStamp;
  timeout = timeout / 1000;
  let perormTime;
  if (timeout >= 3600) {
    perormTime = `${Math.floor(timeout / 3600)}h`;
  } else if (timeout >= 60) {
    perormTime = `${Math.floor(timeout / 60)}min`;
  } else {
    perormTime = `${timeout}s`;
  }
  return perormTime;
}

/**
 * ios 时间初始化问题
 */
export function timeReplace(date) {
  return typeof date === 'string' ? date.replace(/-/gi, '/') : date;
}

/**
 * 返回日期格式 2020-04-13 09:15:14
 * @param {Number | String} val
 * @return {String}
 */
export function formatDate(val, fmt = 'YYYY-mm-dd HH:MM:SS') {
  const date = new Date(timeReplace(val));

  if (isNaN(date.getTime())) {
    console.warn('无效的时间');
    return '';
  }
  const fmtArr = ['Y+', 'm+', 'd+', 'H+', 'M+', 'S+'];
  const opt = {
    'Y+': date.getFullYear().toString(),
    'm+': (date.getMonth() + 1).toString(),
    'd+': date.getDate().toString(),
    'H+': date.getHours().toString(),
    'M+': date.getMinutes().toString(),
    'S+': date.getSeconds().toString(),
  };
  let res;
  let time = fmt;
  fmtArr.forEach((key) => {
    res = new RegExp(`(${key})`).exec(fmt);
    if (res) {
      time = time.replace(res[1], (res[1].length === 1) ? (opt[key]) : (opt[key].padStart(res[1].length, '0')));
    }
  });
  return time;
}

/**
 * 返回日期格式 2020-04-13 09:15:14 或 ''
 * @param val
 * @return {String}
 */
export function modifyFormatDate(val) {
  if (!val) {
    return '';
  }
  return formatDate(val);
}

/**
 * 复制文本
 * @param {String} text
 */
export const copyText = (text) => {
  const textarea = document.createElement('textarea');
  textarea.setAttribute('readonly', '');
  textarea.style.position = 'absolute';
  textarea.style.left = '-9999px';

  document.body.appendChild(textarea);
  textarea.value = text;

  textarea.select();
  let result = false;
  try {
    result = document.execCommand('copy');
  } catch (error) {
    console.warn(error);
  }
  textarea.blur();
  document.body.removeChild(textarea);
  return result;
};
