<template>
  <div class="dropdown-selector-container">
    <template v-for="item in fieldsInfo">
      <PowerSelect
        class="king-select"
        v-test.range="'kingSelect'"
        :key="item.type"
        :value="selectedData[item.value]"
        :list="originData[item.list]"
        :name="item.name"
        @selected="handleSelected(item.type, $event)" />
    </template>
  </div>
</template>

<script>
import PowerSelect from './PowerSelect';

export default {
  components: {
    PowerSelect,
  },
  props: {
    fieldsInfo: {
      type: Array,
      default: () => [],
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
      selectedData: {
        bk_set_ids: [],
        bk_module_ids: [],
        bk_service_ids: [],
        bk_process_names: [],
        bk_process_ids: [],
      },
    };
  },
  methods: {
    /**
     * 下拉列表选择
     * @param {String} type - 哪个下拉列表改变了
     * @param {Array} ids - 下拉选择的值 id 列表
     */
    handleSelected(type, ids) {
      // 选择集群后，需要重新拉取模块列表，因此清除已选择的模块，以此类推
      switch (type) {
        case 'set': // 选择集群
          this.selectedData = {
            bk_set_ids: ids,
            bk_module_ids: [],
            bk_service_ids: [],
            bk_process_names: [],
            bk_process_ids: [],
          };
          break;
        case 'module': // 选择模块
          Object.assign(this.selectedData, {
            bk_module_ids: ids,
            bk_service_ids: [],
            bk_process_names: [],
            bk_process_ids: [],
          });
          break;
        case 'service': // 选择服务实例
          Object.assign(this.selectedData, {
            bk_service_ids: ids,
            bk_process_names: [],
            bk_process_ids: [],
          });
          break;
        case 'processName': // 选择进程别名
          this.selectedData.bk_process_names = ids;
          break;
        case 'processId': // 选择实例ID
          this.selectedData.bk_process_ids = ids;
          break;
      }
      const finalSelectedData = this.filterAllSymbol(this.selectedData);
      const finalIds = ids[0] === '*'
        ? []
        : type === 'module'
          ? this.restoreIdForRepeatName(ids)
          : ids;
      this.$emit('selected', type, finalIds, finalSelectedData);
    },
    // 过滤掉下拉里面的 * 号
    filterAllSymbol(data) {
      const result = {};
      for (const [key, value] of Object.entries(data)) {
        if (value.includes('*')) {
          result[key] = [];
        } else {
          if (key === 'bk_module_ids') {
            result[key] = this.restoreIdForRepeatName(value);
          } else {
            result[key] = value;
          }
        }
      }
      return result;
    },
    // 将模块重复名字的拼接 id 转成正常 id，'1,2,3' => 1, 2, 3
    restoreIdForRepeatName(list) {
      const result = [];
      list.forEach((item) => {
        if (typeof item === 'string') {
          const ids = item.split(',');
          ids.forEach(id => result.push(Number(id)));
        } else {
          result.push(item);
        }
      });
      return result;
    },
    // 对外暴露的方法，环境改变了或点击清除按钮，清除已选择的数据
    clearSelectedData() {
      this.selectedData = {
        bk_set_ids: [],
        bk_module_ids: [],
        bk_service_ids: [],
        bk_process_names: [],
        bk_process_ids: [],
      };
      this.$emit('selected', null, null, this.selectedData);
    },
    /**
     * 对外暴露的方法，回填表达式
     * @param {Object} scope
     * @param {Object} options
     * @param {Boolean} options.silent - no emit event when set value
     */
    setValue(scope) {
      const value = JSON.parse(JSON.stringify(scope));
      this.selectedData = value;
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../css/variable.css';

  .dropdown-selector-container {
    display: flex;
    overflow: hidden;
    width: 850px;

    .king-select {
      background-color: #fff;
      width: calc(100% / 5 - 10px);
      margin-right: 10px;
    }
  }
</style>
