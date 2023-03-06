import Vue from 'vue';

class TextTool {
  canvas = null;
  ctx  = null;
  systemCls = '';
  font = '';
  fontSize = 12;
  fontFamilyZh = '';
  fontFamilyEn = ''; // 英文、数字、符号
  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.init();
  }
  init() {
    const isWin = window.navigator.platform.toLowerCase().indexOf('win') === 0;
    this.systemCls = isWin ? 'win' : 'mac';
    this.fontFamilyZh = isWin ? 'Microsoft YaHei' : 'PingFang SC';
    this.fontFamilyEn = isWin ? 'Arial' : 'Helvetica Neue';
  }
  setFont(font) {
    this.font = font;
    this.ctx.font = font;
  }
  setFontSize(fontSize) {
    this.fontSize = fontSize;
  }
  resetCanvas() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
  }
  getWidth2(text) {
    this.setFont('12px Microsoft YaHei');
    return this.ctx.measureText(text).width;
  }
  getWidth(item) {
    this.setFont(item.font);
    return this.ctx.measureText(item.value).width;
  }
  // extraWidth： padding、margin等已知的额外宽度
  getTextWidth(text, extraWidth = 0) {
    // let width = extraWidth;
    let width = 0;
    try {
      const textArr = `${text}`.split('').map(item => ({
        value: item,
        font: `${this.fontSize}px ${escape(item).indexOf('%u') < 0 ? this.fontFamilyEn : this.fontFamilyZh}`,
      }));
      textArr.forEach((item) => {
        width += this.getWidth(item) + 1; // 每个字符串补1px
      });
    } catch (_) {
      width = 0;
      console.warn(_);
    }
    return Math.ceil(width + extraWidth + 2);
  }
  getHeadWidth(text, config = {}) {
    let realText = text;
    let extraWidth = 0;
    const { extra = 0, padding = 30, margin = 0, filter = false, sortable = false } = config;
    extraWidth = extraWidth + extra + padding + margin;
    if (filter || sortable) {
      if (filter) {
        extraWidth += 14; // 13 + 1
        realText = `${text}\n`;
      }
      if (sortable) {
        extraWidth += 20;
      }
    }
    return this.getTextWidth(realText, extraWidth);
  }
}

export const textTool = new TextTool();

Vue.prototype.$textTool = textTool;
