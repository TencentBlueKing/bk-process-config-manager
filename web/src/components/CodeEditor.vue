<template>
  <div ref="codeEditorRef" class="code-editor" v-test.common="'ide'"></div>
</template>

<script>
import { editor as monacoEditor } from 'monaco-editor';

export default {
  props: {
    content: {
      type: String,
      default: '',
    },
    language: {
      type: String,
      default: 'python',
    },
    readonly: {
      type: Boolean,
      default: true,
    },
    // 行尾
    eol: {
      type: String,
      default: 'LF',
    },
  },
  data() {
    return {
      codeEditor: null,
      layoutTimer: null, // 重新计算编辑器样式
    };
  },
  watch: {
    content(val) {
      this.setValue(val);
      this.layoutEditor(true);
    },
    language(val) {
      monacoEditor.setModelLanguage(this.codeEditor.getModel(), val);
    },
    readonly(val) {
      this.codeEditor.updateOptions({ readOnly: val });
      this.setEditorBackground();
    },
  },
  mounted() {
    this.initEditor();
    this.setEditorBackground();
    window.bus.$on('resize', this.layoutEditor);
    window.bus.$on('navigation-toggle', this.onNavigationToggle);
    window.addEventListener('resize', this.layoutEditor, { passive: true });
  },
  beforeDestroy() {
    window.bus.$off('resize', this.layoutEditor);
    window.bus.$off('navigation-toggle', this.onNavigationToggle);
    window.removeEventListener('resize', this.layoutEditor);
  },
  methods: {
    async initEditor() {
      this.codeEditor = monacoEditor.create(this.$refs.codeEditorRef, {
        theme: 'vs-dark',
        minimap: { enabled: false },
        readOnly: this.readonly,
        value: this.getEolContent(this.content, this.eol),
        language: this.language || 'python',
      });
      this.$emit('change', this.getContent());
      this.codeEditor.onDidChangeModelContent(() => {
        this.$emit('change', this.getContent());
      });
    },
    setEditorBackground() {
      if (this.readonly) {
        this.$refs.codeEditorRef.querySelector('.monaco-editor .margin').style.backgroundColor = 'rgb(46,46,46)'; // 323232
        this.$refs.codeEditorRef.querySelector('.monaco-editor .monaco-editor-background').style.backgroundColor = 'rgb(46,46,46)';
      } else {
        this.$refs.codeEditorRef.querySelector('.monaco-editor .margin').style.backgroundColor = 'rgb(33,33,33)'; // 212121
        this.$refs.codeEditorRef.querySelector('.monaco-editor .monaco-editor-background').style.backgroundColor = 'rgb(29,29,29)'; // 1D1D1D
      }
    },
    onNavigationToggle() {
      setTimeout(() => {
        this.layoutEditor(true);
      }, 300);
    },
    setValue(val) {
      if (this.codeEditor && this.codeEditor.setValue) {
        this.codeEditor.setValue(this.getEolContent(val, this.eol));
      }
    },
    getContent() {
      const val = this.codeEditor.getValue() || '';
      return this.getEolContent(val, this.eol);
    },
    getEolContent(val, eol = 'LF') {
      const lfStr = val.replace(/\r\n/ig, '\n');
      if (eol === 'LF') {
        return lfStr;
      }
      return lfStr.replace(/\n/ig, '\r\n');
    },
    // 窗口 resize 时自动计算样式，如果是父组件元素样式改变(如全屏)，需要手动调用且马上生效，调用此方法参数为 true 禁用防抖
    layoutEditor(immediately) {
      if (this.codeEditor) {
        this.layoutTimer && clearTimeout(this.layoutTimer);
        if (immediately) {
          this.$nextTick(() => {
            this.codeEditor.layout();
          });
        } else {
          this.layoutTimer = setTimeout(() => {
            this.codeEditor.layout();
          }, 200);
        }
      }
    },
  },
};
</script>

<style scoped>
.code-editor {
  height: 100%;
  overflow: hidden;
  background-color: #1d1d1d;
}
</style>
