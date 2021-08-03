<template>
  <div :class="['expression-selector-container', isInputActive && 'active']">
    <div class="power-input-container" ref="inputContainerRef" @click="handleInputClick">
      <template v-for="item in fieldsInfo">
        <PowerInput ref="powerInputRef"
                    :key="item.type"
                    :value="selectedData[item.value]"
                    :list="originData[item.list]"
                    :name="item.name"
                    @change="handleChange(item.type, $event)" />
        <div v-if="item.hasGap" class="gap" :key="item.type + '-gap'">.</div>
      </template>
    </div>
  </div>
</template>

<script>
import PowerInput from './PowerInput';

export default {
  components: {
    PowerInput,
  },
  props: {
    showSelect: {
      type: Boolean,
      default: true,
    },
    fieldsInfo: {
      type: Array,
      required: true,
    },
    originData: {
      type: Object,
      default() {
        return {
          bk_set_list: [],
          bk_module_list: [],
          bk_service_list: [],
          bk_process_name_list: [],
          bk_process_id_list: [],
        };
      },
    },
  },
  data() {
    return {
      isInputActive: false, // 表达式输入框是否激活
      selectedData: {
        bk_set_ids: [],
        bk_module_ids: [],
        bk_service_ids: [],
        bk_process_names: [],
        bk_process_ids: [],
      },
      expressionData: {
        bk_set_name: '*',
        bk_module_name: '*',
        service_instance_name: '*',
        bk_process_name: '*',
        bk_process_id: '*',
      },
    };
  },
  mounted() {
    this.computeComma(false);
    document.addEventListener('click', this.handleDocumentClick);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleDocumentClick);
  },
  methods: {
    // 手动触发 tagInput
    handleInputClick(e) {
      const inputContainer = this.$refs.inputContainerRef;
      if (e.target === inputContainer) {
        inputContainer.lastElementChild.click();
      }
    },
    // 判断 tagInput 是否有激活
    handleDocumentClick() {
      // 如果组件已经激活，200ms后判断是否还是激活状态，200ms 是因为 tag-input 组件内部实现是 200ms 后失活
      const timeout = this.isInputActive ? 200 : 0;
      setTimeout(() => {
        const isEditList = this.$refs.powerInputRef.map(ins => ins.$refs.tagInputRef.isEdit);
        const isInputActive = isEditList.some(Boolean);
        if (this.isInputActive || isInputActive) {
          this.isInputActive = isInputActive;
          this.computeComma(isInputActive);
        }
      }, timeout);
    },
    // 处理逗号
    computeComma(isInputActive) {
      // 隐藏最后一个 tag 后面的逗号
      const tagInputList = this.$el.querySelectorAll('.bk-tag-input .tag-list');
      tagInputList.forEach((tagInput) => {
        const itemList = tagInput.querySelectorAll('.key-node');
        const { length } = itemList;
        itemList.forEach((item, index) => {
          if (index === length - 1) {
            item.classList.add('remove-comma');
          } else {
            item.classList.remove('remove-comma');
          }
        });
      });
      if (isInputActive) {
        // 当前激活的 tag 末尾显示逗号
        const activeItemList = this.$el.querySelectorAll('.bk-tag-input.active .tag-list .key-node');
        activeItemList.forEach((item) => {
          item.classList.remove('remove-comma');
        });
      }
    },
    /**
             * tag 选择
             * @param {String} type - 字段类型
             * @param {Array} ids - 选择的值 id 列表
             */
    handleChange(type, ids) {
      // 选择集群后，需要重新拉取模块列表，因此清除已选择的模块，以此类推 todo 接口还不支持在表达式里面拉取列表
      const idString = ids.length ? ids.join(',') : '*';
      switch (type) {
        case 'set': // 选择集群
          this.selectedData.bk_set_ids = ids;
          this.expressionData.bk_set_name = idString;
          break;
        case 'module': // 选择模块
          this.selectedData.bk_module_ids = ids;
          this.expressionData.bk_module_name = idString;
          break;
        case 'service': // 选择服务实例
          this.selectedData.bk_service_ids = ids;
          this.expressionData.service_instance_name = idString;
          break;
        case 'processName': // 选择进程别名
          this.selectedData.bk_process_names = ids;
          this.expressionData.bk_process_name = idString;
          break;
        case 'processId': // 选择实例ID
          this.selectedData.bk_process_ids = ids;
          this.expressionData.bk_process_id = idString;
          break;
      }
      this.$emit('selected', type, idString, this.expressionData);
    },
    // 对外暴露的方法，点击清除按钮，清除已选择的数据
    clearSelectedData() {
      this.selectedData = {
        bk_set_ids: [],
        bk_module_ids: [],
        bk_service_ids: [],
        bk_process_names: [],
        bk_process_ids: [],
      };
      this.expressionData = {
        bk_set_name: '*',
        bk_module_name: '*',
        service_instance_name: '*',
        bk_process_name: '*',
        bk_process_id: '*',
      };
      this.$emit('selected', null, null, this.expressionData);
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../css/variable.css';

  .expression-selector-container {
    display: flex;
    width: 850px;
    margin-right: 10px;
    border: 1px solid #c4c6cc;
    border-radius: 2px;
    transition: border-color .3s;
    background-color: #fff;

    &.active {
      border-color: $newMainColor;
      transition: border-color .3s;
    }

    .power-input-container {
      display: flex;
      flex-wrap: wrap;
      width: 100%;
      min-height: 30px;
      cursor: pointer;

      .gap {
        flex-shrink: 0;
        width: 12px;
        line-height: 30px;
        text-align: center;
        font-weight: bold;
        background-color: #f5f6fa;
      }
    }
  }
</style>
