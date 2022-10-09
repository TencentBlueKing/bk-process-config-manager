<template>
  <div class="draft-diff-container">
    <div class="draft-diff-header">
      <DiffNav :diff-count="diffCount" @previous="jumpPreviousChange" @next="jumpNextChange" />
    </div>
    <div class="draft-diff-title">
      <div class="draft-diff-title-half">
        <slot name="leftTitle">Old data</slot>
      </div>
      <div class="draft-diff-title-half">
        <slot name="rightTitle">New Data</slot>
      </div>
    </div>
    <DiffEditor ref="diffEditorRef" style="height: calc(100% - 138px);margin: 0 30px 30px;"
                :old-data="oldData" :new-data="newData" :diff-count.sync="diffCount" />
  </div>
</template>

<script>
import DiffNav from '@/components/DiffNav';
import DiffEditor from '@/components/DiffEditor';

export default {
  components: {
    DiffNav,
    DiffEditor,
  },
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
  },
  data() {
    return {
      diffCount: 0,
    };
  },
  methods: {
    jumpNextChange() {
      this.$refs.diffEditorRef.diffNavigator.next();
    },
    jumpPreviousChange() {
      this.$refs.diffEditorRef.diffNavigator.previous();
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../css/variable.css';

  .draft-diff-container {
    height: calc(100vh - 60px);

    .draft-diff-header {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      height: 56px;
      padding-right: 30px;
    }

    .draft-diff-title {
      position: relative;
      z-index: 1;
      display: flex;
      height: 52px;
      margin: 0 30px;
      font-size: 12px;
      line-height: 16px;
      color: #c4c6cc;
      background: #323232;
      box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .3);

      .draft-diff-title-half {
        display: flex;
        align-items: center;
        width: calc(50% - 15px);

        &:first-child {
          border-right: 1px solid $newBlackColor2;
        }
        .status-flag {
          flex-shrink: 0;
          padding: 0 10px;
          text-align: center;
          min-width: 60px;
          line-height: 52px;
          color: $newBlackColor3;
          background: #424242;
        }
        .create-time {
          padding-left: 8px;
        }
      }
    }
  }
</style>
