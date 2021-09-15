<template>
  <div class="expression-input-container" :class="{ 'active': isActive }"
       v-bk-clickoutside="handleClickOutside"
       @click="handleClickContainer">
    <template v-for="item in fieldsInfo">
      <div class="single-input-container" :key="item.type">
        <div class="hold-text">{{ expressionData[item.key] }}</div>
        <input
          v-test.range="'expressionInput'"
          v-model.trim="expressionData[item.key]"
          class="single-input" placeholder="*"
          @change="handleChange(item.type, $event)" />
      </div>
      <div v-if="item.hasGap" class="gap" :key="item.key + '-gap'">.</div>
    </template>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isActive: false,
      fieldsInfo: [ // 列表渲染信息
        { type: 'set', key: 'bk_set_name', hasGap: true },
        { type: 'module', key: 'bk_module_name', hasGap: true },
        { type: 'service', key: 'service_instance_name', hasGap: true },
        { type: 'processName', key: 'bk_process_name', hasGap: true },
        { type: 'processId', key: 'bk_process_id', hasGap: false },
      ],
      expressionData: {
        bk_set_name: '',
        bk_module_name: '',
        service_instance_name: '',
        bk_process_name: '',
        bk_process_id: '',
      },
    };
  },
  methods: {
    handleClickContainer(e) {
      this.isActive = true;
      if (e.target === this.$el) {
        const inputs = this.$el.querySelectorAll('.single-input');
        inputs[inputs.length - 1].focus();
      }
    },
    handleClickOutside() {
      this.isActive = false;
    },
    handleChange(type, e) {
      this.$emit('selected', type, e.target.value, this.expressionData);
    },
    // 对外暴露的方法，点击清除按钮，清除已选择的数据
    clearSelectedData() {
      this.expressionData = {
        bk_set_name: '',
        bk_module_name: '',
        service_instance_name: '',
        bk_process_name: '',
        bk_process_id: '',
      };
      this.$emit('selected', null, null, this.expressionData);
    },
    /**
     * 对外暴露的方法，回填表达式
     * @param {Object} expressionScope
     * @param {Object} options
     * @param {Boolean} options.silent - no emit event when set value
     */
    setValue(expressionScope, { silent }) {
      this.expressionData = expressionScope;
      if (!silent) {
        this.$emit('selected', 'custom', null, this.expressionData);
      } else {
        this.$emit('selected', null, null, this.expressionData);
      }
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../css/variable.css';
  @import '../../css/mixins/scroll.css';

  .expression-input-container {
    display: flex;
    flex-wrap: wrap;
    width: 850px;
    height: 32px;
    margin-right: 10px;
    cursor: pointer;
    border-radius: 2px;
    border: 1px solid #c4c6cc;
    background-color: #fff;
    transition: border-color .3s;
    overflow-y: auto;

    @mixin scroller;

    &.active {
      border-color: $newMainColor;
      transition: border-color .3s;
    }

    .single-input-container {
      position: relative;

      .hold-text {
        padding: 0 12px;
        visibility: hidden;
        height: 30px;
        line-height: 30px;
        min-width: 48px;
        max-width: 400px;
        font-size: 12px;
        overflow: hidden;
      }

      .single-input {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        line-height: 30px;
        padding: 0 12px;
        border: 0;
        font-size: 12px;
        color: $newBlackColor2;

        &::placeholder {
          color: #c4c6cc;
          padding-left: 10px;
        }
      }
    }

    .gap {
      flex-shrink: 0;
      width: 12px;
      height: 30px;
      line-height: 30px;
      text-align: center;
      font-weight: bold;
      background-color: #f5f6fa;
    }
  }
</style>
