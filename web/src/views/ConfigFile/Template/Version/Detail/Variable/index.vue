<template>
  <div class="variable-panel-container" v-test="'variable'">
    <div class="right-panel-header">
      <div class="icon-container" @click="$emit('close')">
        <span class="bk-icon icon-expand-line"></span>
      </div>
      <div class="title">{{ $t('变量') }}</div>
    </div>
    <div class="right-panel-main">
      <!-- <div class="bk-button-group">
        <bk-button class="king-button" @click="toggleTab('global')" :class="activeTab === 'global' && 'is-selected'">
          {{ $t('内置变量') }}
        </bk-button>
      </div> -->
      <bk-input
        v-test="'variableSearch'"
        v-model="keyword"
        :clearable="true"
        class="king-input"
        right-icon="icon-search"
        @change="handleKeywordChange" />
      <div v-bkloading="{ isLoading: searchLoading, opacity: .1 }" class="variable-container" @click="copyText">
        <!-- 全局变量 -->
        <div v-show="activeTab === 'global'" class="table-container">
          <div class="table-header couple-container">
            <span class="couple-left">{{ $t('名称') }}</span>
            <span class="couple-right">{{ $t('变量') }}</span>
          </div>
          <ul class="table-body">
            <template v-for="item in globalVariables">
              <li v-show="item.isShow" class="couple-container" :key="item.key"
                  v-test="'variableItem'" :test-key="item.key">
                <div class="copy-text-container" :data-copy-text="item.key">
                  <span class="text-overflow-row couple-left">{{ item.name }}</span>
                  <span class="text-overflow-row couple-right">{{ item.key }}</span>
                </div>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Tippy from 'bk-magic-vue/lib/utils/tippy';
import 'bk-magic-vue/lib/ui/overflow-tips.css';

export default {
  name: 'HelpVariable',
  data() {
    return {
      keyword: '',
      searchLoading: false,
      inputTimer: null,
      activeTab: 'global', // global
      globalVariables: [],
    };
  },
  watch: {
    '$store.state.cmdb.globalVariables': {
      handler(val) {
        this.globalVariables = val.map(item => ({
          key: item.bk_property_id,
          name: item.bk_property_name,
          isShow: true,
        }));
      },
      immediate: true,
    },
  },
  created() {
    if (!this.$store.state.cmdb.globalVariables.length) {
      this.$store.dispatch('cmdb/ajaxGetGlobalVariables');
    }
  },
  methods: {
    toggleTab(tab) {
      this.keyword = '';
      this.activeTab = tab;
      this.matchKeyword(true);
    },
    handleKeywordChange() {
      this.matchKeyword();
    },
    matchKeyword(immediately) {
      if (!immediately) {
        this.searchLoading = true;
      }
      this.inputTimer && clearTimeout(this.inputTimer);
      this.inputTimer = setTimeout(() => {
        this.searchLoading = false;
        this.globalVariables.forEach((item) => {
          let variableKeyAndName = '';
          Object.entries(item).forEach(([key, value]) => {
            if (key !== 'isShow') {
              variableKeyAndName += value;
            }
          });
          item.isShow = variableKeyAndName.toLowerCase().includes(this.keyword.toLowerCase());
        });
      }, immediately ? 0 : 300);
    },
    copyText(e) {
      const el = this.findCopyElement(e);
      if (el) {
        try {
          // 复制文本，复制变量时需要在变量外层加上花括号
          const input = document.createElement('input');
          const content = el.getAttribute('data-copy-text');
          input.setAttribute('value', `\${${content}}`);
          document.body.appendChild(input);
          input.select();
          document.execCommand('copy');
          document.body.removeChild(input);

          // 文本背景样式
          el.classList.add('copy');
          setTimeout(() => {
            window.addEventListener('click', (onceEvent) => {
              if (this.findCopyElement(onceEvent) !== el) {
                el.classList.remove('copy');
              }
            }, { once: true });
          });

          // 显示tippy
          if (!el._tippy) {
            el._tippy = Tippy(el, {
              content: this.$t('复制成功'),
              placement: 'bottom',
              trigger: 'manual',
              arrow: true,
              size: 'small',
              extCls: 'copy-successfully-tippy',
            });
          }
          el._tippy.show();
        } catch (err) {
          console.warn(err);
        }
      }
    },
    /**
             * 点击事件是否在复制的元素容器上触发，是就返回复制文本的元素容器
             * @param {MouseEvent} e
             */
    findCopyElement(e) {
      let el = e.target;
      while (el !== null && !el.classList.value.includes('copy-text-container')) {
        el = el.parentElement;
      }
      return el;
    },
  },
};
</script>

<style lang="postcss">
  .copy-successfully-tippy .tippy-tooltip {
    background-color: rgba(0, 0, 0, .9) !important;

    .tippy-arrow {
      border-bottom-color: rgba(0, 0, 0, .9) !important;
    }
  }
</style>

<style scoped lang="postcss">
  @import '../../../../../../css/variable.css';
  @import '../../../../../../css/mixins/scroll.css';

  .variable-panel-container {
    position: relative;
    display: flex;
    flex-flow: column;
    height: 100%;
    color: #dcdee5;

    .right-panel-main {
      height: 100%;
      padding: 0 24px;
      overflow: hidden;

      /*.bk-button-group {
        padding-top: 14px;
        width: 100%;
        .king-button {
            width: 100%;
            background: #323232;
            color: #C4C6CC;
            border-color: $newBlackColor2;
            &:hover, &.is-selected {
                color: #DCDEE5;
                border-color: $newMainColor;
            }
            &.is-selected {
                background: #192845;
            }
        }
      }*/
      .king-input {
        width: 100%;
        padding: 14px 0;

        /deep/ input {
          color: #dcdee5;
          background: #323232 !important;
          border-color: $newBlackColor2;

          &::placeholder {
            color: $newBlackColor2;
          }

          &:focus,
          &:hover {
            border-color: #dcdee5 !important;
          }
        }

        /deep/ .bk-icon {
          color: $newBlackColor2;
        }
      }

      .variable-container {
        height: calc(100% - 80px);

        .table-container {
          height: 100%;

          .couple-container {
            display: flex;
            align-items: center;
            height: 32px;
            padding: 3px 0;
            line-height: 25px;
            color: #c4c6cc;
            font-size: 12px;
            border-bottom: 1px solid #4a4a4a;

            .couple-left {
              width: 40%;
              padding: 0 9px;
            }

            .couple-right {
              width: 60%;
              padding: 0 9px;
            }
          }

          .table-header {
            color: #dcdee5;
            background: #53545c;
            border-bottom: 0;
          }

          .table-body {
            height: calc(100% - 32px);
            overflow: auto;

            @mixin scroller;

            .copy-text-container {
              display: flex;
              width: 100%;
              height: 26px;
              cursor: pointer;
              border-radius: 2px;

              &.copy,
              &:hover {
                background-color: #44454d;
              }
            }
          }
        }
      }
    }
  }
</style>
