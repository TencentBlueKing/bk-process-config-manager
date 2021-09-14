<template>
  <div ref="diffEditorRef" class="diff-editor"></div>
</template>

<script>
import { editor as monacoEditor } from 'monaco-editor';

export default {
  props: {
    oldData: {
      type: Object,
      default() {
        return {
          content: '',
          language: 'python',
        };
      },
    },
    newData: {
      type: Object,
      default() {
        return {
          content: '',
          language: 'python',
        };
      },
    },
    diffCount: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      diffEditor: null,
      diffNavigator: null,
      layoutTimer: null, // 重新计算编辑器样式
    };
  },
  mounted() {
    this.initDiffEditor();
    window.bus.$on('navigation-toggle', this.onNavigationToggle);
    window.addEventListener('resize', this.layoutEditor, { passive: true });
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.layoutEditor);
    window.bus.$off('navigation-toggle', this.onNavigationToggle);
    this.diffCountTimer && clearTimeout(this.diffCountTimer);
  },
  methods: {
    initDiffEditor() {
      const originalModel = monacoEditor.createModel(this.oldData.content, this.oldData.language || 'python');
      const modifiedModel = monacoEditor.createModel(this.newData.content, this.newData.language || 'python');

      const diffEditor = monacoEditor.createDiffEditor(this.$refs.diffEditorRef, {
        readOnly: true,
        theme: 'vs-dark',
      });
      diffEditor.setModel({
        original: originalModel,
        modified: modifiedModel,
      });
      this.diffEditor = diffEditor;
      this.diffNavigator = monacoEditor.createDiffNavigator(diffEditor, {
        followsCaret: false, // resets the navigator state when the user selects something in the editor
        ignoreCharChanges: true, // jump from line to line
      });
      this.computeDiffCount();
    },
    computeDiffCount() { // 计算有 n 处不同
      this.diffCountTimer = setTimeout(() => {
        const changes = this.diffEditor.getLineChanges();
        if (changes) {
          this.$emit('update:diffCount', changes.length);
        } else {
          this.computeDiffCount();
        }
      }, 40);
    },
    onNavigationToggle() {
      setTimeout(() => {
        this.layoutEditor(true);
      }, 300);
    },
    // 窗口 resize 时自动计算样式，如果是父组件元素样式改变(如全屏)，需要手动调用且马上生效，调用此方法参数为 true 禁用防抖
    layoutEditor(immediately) {
      if (this.diffEditor) {
        this.layoutTimer && clearTimeout(this.layoutTimer);
        if (immediately) {
          this.$nextTick(() => {
            this.diffEditor.layout();
          });
        } else {
          this.layoutTimer = setTimeout(() => {
            this.diffEditor.layout();
          }, 200);
        }
      }
    },
  },
};
</script>

<style scoped lang="postcss">
  .diff-editor {
    height: 100%;
    overflow: hidden;
    background-color: #1d1d1d;

    /deep/ .monaco-editor {
      .margin {
        background-color: #212121 !important;
      }

      .monaco-editor-background {
        background-color: #1d1d1d !important;
      }
    }
  }
</style>
