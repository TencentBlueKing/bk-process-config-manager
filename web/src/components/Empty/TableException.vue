<template>
  <bk-exception class="exception-box" :scene="scene" :type="typeDisplay">
    <template v-if="['search-empty', '500'].includes(typeDisplay)" #default>
      <template v-if="typeDisplay === 'search-empty'">
        <p class="empty-title">{{ $t('搜索结果为空') }}</p>
        <i18n tag="p" class="empty-desc" path="可以尝试调整关键词或清空筛选条件">
          <bk-link theme="primary" class="empty-btn" @click="() => handleClick('clear')">
            {{ $t('清空筛选条件') }}
          </bk-link>
        </i18n>
      </template>
      <template v-if="typeDisplay === '500'">
        <div class="empty">
          <p class="empty-title">{{ $t('获取数据异常') }}</p>
          <p class="empty-desc">
            <bk-link theme="primary" class="empty-btn" @click="() => handleClick('refresh')">
              {{ $t('刷新') }}
            </bk-link>
          </p>
        </div>
      </template>
    </template>
  </bk-exception>
</template>
<script lang="ts">
export default {
  name: 'TableException',
  props: {
    type: {
      type: String,
      default: 'empty',
    },
    delay: {
      type: Boolean,
      default: false,
    },
    scene: {
      type: String,
      default: 'part',
    },
  },
  data() {
    return {
      oldType: this.type,
    };
  },
  computed: {
    typeDisplay() {
      return this.delay ? this.oldType : this.type;
    },
  },
  watch: {
    delay: {
      handler(val) {
        if (!val) {
          this.oldType = this.type;
        }
      },
      immediate: true,
    },
  },
  methods: {
    handleClick(clickType) {
      this.$emit(`empty-${clickType}`);
    },
  },
};
</script>

<style lang="postcss" scoped>
  .empty-title {
    line-height: 22px;
    font-size: 14px;
    color: #63656e;
  }

  .empty-desc {
    display: flex;
    align-items: center;
    margin-top: 8px;
    line-height: 20px;
    font-size: 12px;
    color: #979ba5;
  }
  .empty-btn {
    margin-left: 4px;
    /deep/ .bk-link-text {
      font-size: 12px;
    }
  }
</style>
