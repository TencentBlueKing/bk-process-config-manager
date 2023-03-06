<template>
  <div class="select-instance-container" v-test.range="'wrapper'">
    <!-- 环境选择 -->
    <div v-bk-tooltips="envTips" class="env-container">
      <bk-select
        v-test.range="'env'"
        v-model="setEnv"
        class="king-select-env"
        prefix-icon="gsekit-icon gsekit-icon-environment-2"
        :clearable="false"
        @selected="handleEnvChange">
        <bk-option id="1" :name="$t('测试')"></bk-option>
        <bk-option id="2" :name="$t('体验')"></bk-option>
        <bk-option id="3" :name="$t('正式')"></bk-option>
      </bk-select>
    </div>
    <div class="env-gap"></div>
    <!-- 筛选 -->
    <DropdownSelector
      v-show="isDropdownMode"
      ref="dropdownSelectorRef"
      :fields-info="fieldsInfo"
      :origin-data="dropdownSelectorData"
      @selected="handleDropdownChange" />
    <!-- 表达式 -->
    <ExpressionInput v-show="!isDropdownMode" ref="expressionSelectorRef" @selected="handleExpressionChange" />
    <!-- 选择按钮 -->
    <bk-button
      v-test.form="'submit'"
      v-if="showButton"
      class="king-button"
      theme="primary"
      :loading="basicLoading || buttonLoading"
      @click="emitEventWithCurrentValue('buttonClick')">
      {{ $t('选择') }}
    </bk-button>
    <!-- 切换表达式和筛选 -->
    <div class="button-text" style="margin-right: 16px;" v-test.range="'mode'" @click="toggleSelect">
      <span class="gsekit-icon gsekit-icon-switch-line"></span>
      {{ isDropdownMode ? $t('表达式') : $t('筛选') }}
    </div>
    <div class="button-text" :class="{ 'is-hidden': isClearDisabled }" v-test.range="'clear'" @click="clearSelect">
      <span class="bk-icon icon-delete"></span>
      {{ $t('清空') }}
    </div>
  </div>
</template>

<script>
// 本组件(非受控组件)发出的事件：
// 1. buttonClick，点击选择按钮事件，参数为(是否为筛选下拉模式，当前模式已选数据)
// 2. valueChange，筛选或表达式选择事件(包括清空、切换环境)，参数为(是否为筛选下拉模式，当前模式已选数据)
// 3. init，组件初始化，参数为(是否为筛选下拉模式，当前模式已选数据)
import DropdownSelector from './DropdownSelector';
import ExpressionInput from './ExpressionInput';
import { bus } from '@/common/bus';

export default {
  components: {
    DropdownSelector,
    ExpressionInput,
  },
  props: {
    showButton: { // 按钮：选择
      type: Boolean,
      default: false,
    },
    buttonLoading: {
      type: Boolean,
      default: false,
    },
    dropdownMode: {
      type: Boolean,
      default: true,
    },
    defaultSelected: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      inited: false,
      basicLoading: false, // 获取下拉列表数据时候给按钮加载状态
      isDropdownMode: this.dropdownMode, // 筛选下拉模式，反之表达式模式
      setEnv: '', // 集群环境，默认为正式
      envTips: {
        content: this.$t('环境类型，对应配置平台中的集群属性。进程筛选范围受限于此属性'),
        delay: 3000,
      },
      fieldsInfo: [ // 列表渲染信息
        { type: 'set', value: 'bk_set_ids', list: 'bk_set_list', name: this.$t('集群'), hasGap: true },
        { type: 'module', value: 'bk_module_ids', list: 'bk_module_list', name: this.$t('模块'), hasGap: true },
        { type: 'service', value: 'bk_service_ids', list: 'bk_service_list', name: this.$t('服务实例'), hasGap: true },
        { type: 'processName', value: 'bk_process_names', list: 'bk_process_name_list', name: this.$t('进程别名'), hasGap: true },
        { type: 'processId', value: 'bk_process_ids', list: 'bk_process_id_list', name: 'process_id', hasGap: false },
      ],
      sourceDropdownSelected: {},
      dropdownSelectorData: { // 筛选可选项
        bk_set_list: [],
        bk_module_list: [],
        bk_service_list: [],
        bk_process_name_list: [],
        bk_process_id_list: [],
      },
      dropdownSelectedData: { // 记录筛选组件选择的值，计算是否显示清空
        bk_set_ids: [],
        bk_module_ids: [],
        bk_service_ids: [],
        bk_process_names: [],
        bk_process_ids: [],
      },
      expressionSelectedData: { // 记录表达式组件选择的值，计算是否显示清空
        bk_set_name: '*',
        bk_module_name: '*',
        service_instance_name: '*',
        bk_process_name: '*',
        bk_process_id: '*',
      },
      bizId: null,
      bizEnvMap: {},
    };
  },
  computed: {
    isClearDisabled() { // 如果已选值为空则不显示清空按钮
      const isEmptied = this.isDropdownMode
        ? Object.values(this.dropdownSelectedData).every(item => item.length === 0)
        : Object.values(this.expressionSelectedData).every(item => item === '*');
      this.$emit('update:isExisted', !isEmptied);
      return isEmptied;
    },
  },
  created() {
    bus.$on('clear-select-filter', this.clearSelect);
    this.bizId = this.$store.state.bizId;
    this.bizEnvMap = JSON.parse(window.localStorage.getItem('BK_SET_ENV_MAP') || '{}');
    this.setEnv = this.bizEnvMap[this.bizId] || '3';
    if (this.isDropdownMode) {
      this.setSelectedData();
    } else if (Object.keys(this.defaultSelected).length) {
      this.expressionSelectedData = { ...this.defaultSelected };
    }
    setTimeout(() => {
      // 初始化时就通过父组件设置值时，保证只初始化一次列表
      if (!this.inited) {
        const { bk_set_ids: sets, bk_module_ids: modules, bk_service_ids: services } = this.dropdownSelectedData;
        this.initSelectList(sets, modules, services);
      }
    });
    this.$emit('init', this.isDropdownMode, Object.assign({
      bk_set_env: this.setEnv,
    }, this.isDropdownMode ? { ...this.dropdownSelectedData } : { ...this.expressionSelectedData }));
  },
  mounted() {
    if (this.isDropdownMode) {
      this.$refs.dropdownSelectorRef.setValue(this.sourceDropdownSelected, { silent: true });
    }
  },
  beforeDestroy() {
    bus.$off('clear-select-filter', this.clearSelect);
  },
  methods: {
    // 初始化、环境改变时获取所有下拉列表
    async initSelectList(bkSetIds, bkModuleIds, bkServiceIds) {
      this.basicLoading = true;
      await Promise.all([
        this.fetchSetList(),
        this.fetchModuleList(bkSetIds),
        this.fetchServiceList(bkModuleIds),
        this.fetchProcessList(bkServiceIds),
      ]);
      this.basicLoading = false;
    },
    // 获取集群列表
    async fetchSetList() {
      try {
        this.dropdownSelectorData.bk_set_list = [];
        const res = await this.$store.dispatch('cmdb/ajaxGetSetListByEnv', {
          setEnv: this.setEnv,
        });
        this.dropdownSelectorData.bk_set_list = Object.freeze(res.data.map(item => ({
          id: item.bk_set_id,
          name: item.bk_set_name,
        })));
      } catch (e) {
        console.warn(e);
      }
    },
    // 获取模块列表
    async fetchModuleList(bkSetIds = []) {
      // 做个缓存，如果上次请求的是所有集群下的所有模块，下次还是，就不重复请求了
      const isAllModule = !bkSetIds.length;
      if (isAllModule && this.isAllModuleCache) {
        return;
      }
      try {
        this.dropdownSelectorData.bk_module_list = [];
        const res = await this.$store.dispatch('cmdb/ajaxGetModuleListBySet', {
          data: {
            bk_set_ids: bkSetIds,
          },
        });
        // 根据 bk_module_name 去重
        const idKey = 'bk_module_id';
        const nameKey = 'bk_module_name';
        const noRepeatNameMap = new Map();
        res.data.forEach((item) => {
          const name = item[nameKey];
          const existModule = noRepeatNameMap.get(name);
          if (existModule) {
            existModule.id += `,${item[idKey]}`; // 如果有重复的，id 会变成字符串
          } else {
            noRepeatNameMap.set(name, {
              id: item[idKey], // 数值
              name: item[nameKey],
            });
          }
        });
        this.dropdownSelectorData.bk_module_list = Object.freeze([...noRepeatNameMap.values()]);
        this.isAllModuleCache = isAllModule;
      } catch (e) {
        console.warn(e);
      }
    },
    // 获取服务实例列表
    async fetchServiceList(bkModuleIds = []) {
      // 做个缓存，如果上次请求的是所有模块下的所有服务实例，下次还是，就不重复请求了
      const isAllService = !bkModuleIds.length;
      if (isAllService && this.isAllServiceCache) {
        return;
      }
      try {
        this.dropdownSelectorData.bk_service_list = [];
        const res = await this.$store.dispatch('cmdb/ajaxGetServiceListByModule', {
          data: {
            bk_module_ids: bkModuleIds,
          },
        });
        this.dropdownSelectorData.bk_service_list = Object.freeze(res.data.map(item => ({
          id: item.service_instance_id,
          name: item.service_instance_name,
        })));
        this.isAllServiceCache = isAllService;
      } catch (e) {
        console.warn(e);
      }
    },
    // 获取进程实例列表概要信息
    async fetchProcessList(bkServiceIds = []) {
      // 做个缓存，如果上次请求的是所有服务实例下的所有进程，下次还是，就不重复请求了
      const isAllProcess = !bkServiceIds.length;
      if (isAllProcess && this.isAllProcessCache) {
        return;
      }
      try {
        this.dropdownSelectorData.bk_process_name_list = [];
        this.dropdownSelectorData.bk_process_id_list = [];
        const res = await this.$store.dispatch('process/ajaxGetProcessListByService', {
          data: {
            service_instance_ids: bkServiceIds,
          },
        });
        // 进程名需要去重
        const processNames = res.data.map(item => item.bk_process_name);
        const noRepeatNames = [...new Set(processNames)];
        this.dropdownSelectorData.bk_process_name_list = Object.freeze(noRepeatNames.map(name => ({ id: name, name })));
        this.dropdownSelectorData.bk_process_id_list = Object.freeze(res.data.map(item => ({
          id: item.bk_process_id,
          name: String(item.bk_process_id),
        })));
        this.isAllProcessCache = isAllProcess;
      } catch (e) {
        console.warn(e);
      }
    },

    // 环境改变
    handleEnvChange(value) {
      this.bizEnvMap[this.bizId] = value;
      localStorage.setItem('BK_SET_ENV_MAP', JSON.stringify(this.bizEnvMap));
      // 清空组件已选择的数据，更新相关下拉列表
      this.$refs.dropdownSelectorRef.clearSelectedData();
      this.$refs.expressionSelectorRef.clearSelectedData();
      this.initSelectList();
      // 触发事件
      this.emitEventWithCurrentValue('valueChange');
    },
    /**
     * 筛选下拉变化
     * @param {String|null} type - 哪个下拉列表改变了，清空时为 null，主动设置为 null 或 'custom'
     * @param {Array|null} ids - 下拉选择的值 id 列表，清空时为 null，主动设置为 null
     * @param {Object} selectedData - 所有下拉选择数据
     */
    async handleDropdownChange(type, ids, selectedData) {
      this.dropdownSelectedData = selectedData;
      if (type !== null) {
        this.$emit('valueChange', this.isDropdownMode, {
          bk_set_env: this.setEnv,
          ...selectedData,
        });
        this.basicLoading = true;
        switch (type) {
          case 'set': // 选择集群
            await Promise.all([this.fetchModuleList(ids), this.fetchServiceList(), this.fetchProcessList()]);
            break;
          case 'module': // 选择模块
            await Promise.all([this.fetchServiceList(ids), this.fetchProcessList()]);
            break;
          case 'service': // 选择服务实例
            await this.fetchProcessList(ids);
            break;
        }
        this.basicLoading = false;
      }
    },
    /**
     * 表达式变化
     * @param {String|null} type - 哪个下拉列表改变了，清空时为 null，主动设置为 null 或 'custom'
     * @param {String|null} ids - 单个字段的表单输入值，清空时为 null，主动设置为 null
     * @param {Object} selectedData - 所有输入的表达式数据
     */
    handleExpressionChange(type, ids, selectedData) {
      const result = {};
      for (const [key, value] of Object.entries(selectedData)) {
        result[key] = value === '' ? '*' : value;
      }
      this.expressionSelectedData = result;
      if (type !== null) {
        this.$emit('valueChange', this.isDropdownMode, {
          bk_set_env: this.setEnv,
          ...result,
        });
      }
    },
    // 清空已选择
    clearSelect() {
      if (this.isClearDisabled) {
        return;
      }
      // 清空当前组件已选择的数据和相关下拉列表
      if (this.isDropdownMode) {
        this.$refs.dropdownSelectorRef.clearSelectedData();
        this.basicLoading = true;
        Promise.all([
          this.fetchModuleList(),
          this.fetchServiceList(),
          this.fetchProcessList(),
        ]).then(() => {
          this.basicLoading = false;
        });
      } else {
        this.$refs.expressionSelectorRef.clearSelectedData();
      }
      // 触发事件
      this.emitEventWithCurrentValue('valueChange');
    },
    // 根据当前组件值触发相关事件
    emitEventWithCurrentValue(eventName) {
      const selectedData = this.isDropdownMode ? this.dropdownSelectedData : this.expressionSelectedData;
      this.$emit(eventName, this.isDropdownMode, {
        bk_set_env: this.setEnv,
        ...selectedData,
      });
    },
    // 表达式和筛选切换
    toggleSelect() {
      this.isDropdownMode = !this.isDropdownMode;
      this.emitEventWithCurrentValue('valueChange');
    },

    /**
     * 对外暴露的方法，回填表达式
     * @param {Object} expressionScope
     * @param {Object} options
     * @param {Boolean} options.silent - no emit event when set value
     */
    setExpressionValue(expressionScope, options = { silent: false }) {
      const value = JSON.parse(JSON.stringify(expressionScope));
      this.isDropdownMode = false;
      const newEnv = value.bk_set_env;
      if (newEnv !== this.setEnv) {
        this.setEnv = newEnv;
        this.$refs.dropdownSelectorRef.clearSelectedData();
        this.$refs.expressionSelectorRef.clearSelectedData();
        this.initSelectList();
        this.inited = true;
      }
      delete value.bk_set_env;
      this.$refs.expressionSelectorRef.setValue(value, options);
    },
    /**
     * 对外暴露的方法，回填筛选
     * @param {Object} scope
     * @param {Object} options
     * @param {Boolean} options.silent - no emit event when set value
     */
    setScopeValue(scope, options = { silent: false }) {
      const value = JSON.parse(JSON.stringify(scope));
      this.isDropdownMode = true;
      const newEnv = value.bk_set_env;
      if (newEnv !== this.setEnv) {
        this.setEnv = newEnv;
        this.$refs.dropdownSelectorRef.clearSelectedData();
        this.$refs.expressionSelectorRef.clearSelectedData();
        this.initSelectList();
        this.inited = true;
      }
      delete value.bk_set_env;
      this.setSelectedData(scope);
      this.$refs.dropdownSelectorRef.setValue(this.sourceDropdownSelected, options);
    },
    /**
     * 设置setEnv (遍历环境检查进程之后需要同步当前环境)
     */
    handleSetEnv(value) {
      this.setEnv = value;
    },
    // 设置实际生效的选项值
    setSelectedData(selected) {
      const { fieldsInfo, defaultSelected } = this;
      const selectedData = selected || defaultSelected;
      const defaultValMap = {};
      fieldsInfo.forEach(({ value }) => {
        if (selectedData[value] && selectedData[value].length) {
          const selected = [];
          selectedData[value].reduce((arr, item) => {
            if (typeof item === 'string' && item.indexOf(',') > -1) {
              arr.splice(0, arr.length, ...item.split(',').map(id => parseInt(id, 10)));
            } else {
              arr.push(item);
            }
            return arr;
          }, selected);
          defaultValMap[value] = selected;
        } else {
          defaultValMap[value] = [];
        }
        // 同时设置正确的返回值
        this.sourceDropdownSelected[value] = selectedData[value] || [];
      });
      this.dropdownSelectedData = defaultValMap;
    },
    /**
     * 返回准确的选中值的类型。部分选项 [1,2,3,4,5,6] => [1, 2,'3,4,5,6']
     */
    getFormatScope() {
      if (this.isDropdownMode) {
        const scope = { bk_set_env: this.setEnv };
        const { dropdownSelectedData, fieldsInfo, dropdownSelectorData = [] } = this;
        fieldsInfo.forEach(({ value, list }) => {
          scope[value] = this.getSelectorDefaultValue(dropdownSelectorData[list], dropdownSelectedData[value]);
        });
        return scope;
      }
      return { ...this.expressionSelectedData, bk_set_env: this.setEnv };
    },
    /**
     * 找出id未拼接类型的选项
     */
    getSelectorDefaultValue(list, values) {
      const checked = [];
      list.forEach(({ id }) => {
        if (typeof id === 'string' && id.indexOf(',') > -1) {
          const ids = id.split(',').map(id => parseInt(id, 10));
          if (ids.every(id => values.includes(id))) {
            checked.push(id);
          }
        } else if (values.includes(id)) {
          checked.push(id);
        }
      });
      return checked;
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../css/variable.css';

  .select-instance-container {
    display: flex;
    align-items: center;
    padding: 0 60px;
    height: 72px;
    line-height: 20px;
    font-size: 14px;
    color: $newBlackColor2;
    overflow: hidden;

    .left-title {
      flex-shrink: 0;

      .star {
        color: #ea3636;
        margin: 0 13px 0 4px;
      }
    }

    .env-container {
      flex-shrink: 0;

      .king-select-env {
        background-color: #fff;

        /deep/ .gsekit-icon-environment-2 {
          font-size: 16px;
          left: 8px;
          top: 7px;
          color: $newBlackColor3;
        }

        /deep/ .bk-select-name {
          padding-left: 32px;
        }
      }
    }

    .env-gap {
      flex-shrink: 0;
      width: 1px;
      height: 16px;
      margin: 0 10px;
      background-color: #dcdee5;
    }

    .king-button {
      flex-shrink: 0;
      width: 86px;
      margin-right: 10px;
    }

    .button-text {
      flex-shrink: 0;

      .gsekit-icon-switch-line,
      .icon-delete {
        font-size: 16px;
      }

      &.is-hidden {
        opacity: 0;
        cursor: default;
      }
    }
  }
</style>
