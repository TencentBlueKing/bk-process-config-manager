// 非通用 startDir - 起始位置
export const throttle = function (func, delay) {
  let timer = null;
  return function () {
    const context = this;
    const args = arguments;
    if (!timer) {
      timer = setTimeout(() => {
        func.apply(context, args);
        timer = null;
      }, delay);
    }
  };
};

export const Drag = function (el, startDir = 'left', callFn, timely = false) {
  this.isMouseDown = false;
  const reverseDirMap = {
    left: 'right',
    right: 'left',
    top: 'bottom',
    bottom: 'top',
  };
  const that = this;
  el.onmousedown = function (e) {
    e = e || event;
    let startX = e.clientX;
    let startY = e.clientY;
    that.isMouseDown = true;
    // 原有的css
    const defaultAttrMap = {
      [startDir]: el.style[startDir],
      zIndex: el.style.zIndex || 5,
      position: el.style.position,
    };
    let endX;
    let endY;
    const reverseDir = reverseDirMap[startDir];
    if (timely) {
      Object.keys(reverseDirMap).forEach((dir) => {
        el.style[dir] = 0;
      });
      el.style.position = 'fixed';
    } else {
      el.style[reverseDir] = 0;
      el.style.border = '1px dashed #dae0e4';
    }
    el.style.zIndex = '99999';
    document.onmousemove = function (e) {
      e = e || event;
      endX = e.clientX;
      endY = e.clientY;
      switch (startDir) {
        case 'left':
          el.style.left = `${endX - startX}px`;
          break;
        case 'right':
          el.style.right = `${startX - endX}px`;
          break;
        case 'top':
          el.style.top = `${endY - startY}px`;
          break;
        case 'bottom':
          el.style.bottom = `${startY - endY}px`;
          break;
        default:
          el.style.left = `${endX - startX}px`;
          break;
      }
      if (timely && callFn && typeof callFn === 'function') {
        throttle(callFn({ x: endX - startX, y: endY - startY }, 50));
        startX = endX;
        startY = endY;
      }
    };
    el.onmouseup = function () {
      // 恢复默认值
      el.style.border = '0';
      el.style.zIndex = defaultAttrMap.zIndex;
      el.style[startDir] = defaultAttrMap[startDir];
      el.style.position = defaultAttrMap.position;
      el.style[reverseDir] = 'auto';
      if (!timely && callFn && typeof callFn === 'function') {
        callFn({ x: endX - startX, y: endY - startY });
      }
      that.isMouseDown = false;
      document.onmousemove = null;
    };
    return false;
  };
};
