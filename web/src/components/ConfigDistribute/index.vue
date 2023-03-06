<template>
  <div class="config-file-template-distribute-container"
       v-test.release="'release'" v-bkloading="{ isLoading: fakeLoading }">
    <div class="distribute-above">
      <!-- 步骤显示 -->
      <div class="steps-container" v-if="!isConfigCheck">
        <bk-steps class="king-steps" :cur-step="curStep" :steps="steps"></bk-steps>
      </div>
      <!-- 第一步选择范围 -->
      <!-- 进程范围 -->
      <div class="form-container" v-show="curStep === 1">
        <span class="star-title">{{ $t('进程范围') }}</span>
        <SelectInstance
          ref="selectInstanceRef"
          :dropdown-mode="isDropdownMode"
          :default-selected="selectedScope || {}"
          @init="initSelectData"
          @valueChange="handleSelectInstance" />
      </div>
      <!-- 配置模板，从进程管理进来才需要选择配置模板 -->
      <div class="form-container" v-if="curStep === 1 && isMultipleTemplates">
        <span class="star-title">{{ $t('配置模板') }}</span>
        <bk-select
          class="king-select"
          v-test.release="'tempSelect'"
          searchable
          multiple
          display-tag
          show-select-all
          v-model="selectedTemplateIds"
          @change="handleSelectTemplate">
          <template v-for="option in validTemplates">
            <bk-option
              :key="option.config_template_id"
              :id="option.config_template_id"
              :name="option.template_name">
            </bk-option>
          </template>
        </bk-select>
      </div>
      <!-- 第二步配置生成上方的按钮 -->
      <div class="buttons-above" v-show="curStep === 2">
        <bk-button
          style="margin-right: 10px;"
          v-test.release="'generateAll'"
          :loading="generateLoading"
          :disabled="isTasking"
          @click="handleGenerateAll">
          {{ $t('全部重新生成') }}
        </bk-button>
        <bk-button
          v-test.release="'generateFailAll'"
          :loading="generateFailureLoading"
          :disabled="isTasking || isAllGeneratedSuccess"
          @click="handleGenerateFailure">
          {{ $t('重试所有失败项') }}
        </bk-button>
      </div>
    </div>

    <div class="distribute-below" v-bkloading="{ isLoading: basicLoading, opacity: 1, zIndex: 0 }">
      <!-- 实例表格 -->
      <div class="instance-table-container">
        <template v-for="temp in selectedTemplates">
          <InstanceTable
            :key="temp.config_template_id"
            :ref="`tableRef_${temp.config_template_id}`"
            :action="action"
            :cur-step="curStep"
            :origin-list="instanceTotalList[temp.config_template_id]"
            :is-tasking.sync="isTasking"
            :is-dropdown-mode="isDropdownMode"
            :selected-scope="selectedScope"
            :config-template="temp"
            :max-height="maxHeight"
            @update-version="updateInstanceVersion" />
        </template>
      </div>

      <!-- 下面的操作按钮 -->
      <!-- 第一步(下一步，取消)，第二步(立即下发,上一步，取消) -->
      <div class="buttons-below" v-show="!basicLoading">
        <bk-button
          v-if="isConfigCheck"
          v-test.configCheck="'execute'"
          theme="primary"
          style="min-width: 120px;margin-right: 10px;"
          @click="handleDistribute">
          {{ $t('立即执行') }}
        </bk-button>
        <template v-else>
          <bk-button
            v-show="curStep === 1"
            v-test.common="'stepNext'"
            theme="primary"
            style="min-width: 120px;margin-right: 10px;"
            :disabled="!canNextStep"
            @click="handleNext">
            {{ $t('下一步') }}
          </bk-button>
          <div v-show="curStep === 2" v-bk-tooltips="{ content: $t('所有配置生成成功方能下发'), disabled: isAllGeneratedSuccess }">
            <bk-button
              theme="primary"
              style="min-width: 120px;margin-right: 10px;"
              v-test.form="'submit'"
              :loading="distributeLoading"
              :disabled="isTasking || !isAllGeneratedSuccess"
              @click="handleDistribute">
              {{ $t('立即下发') }}
            </bk-button>
          </div>
          <bk-button
            v-show="curStep === 2"
            v-test.common="'stepPrev'"
            style="min-width: 86px;margin-right: 10px;"
            :disabled="isTasking"
            @click="handlePrevious">
            {{ $t('上一步') }}
          </bk-button>
        </template>
        <bk-button style="min-width: 86px;" @click="handleCancel">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </div>
  </div>
</template>

<script>
import SelectInstance from '@/components/SelectInstance';
import InstanceTable from './InstanceTable';

export default {
  name: 'ConfigDistribute',
  components: {
    SelectInstance,
    InstanceTable,
  },
  props: {
    action: {
      type: String,
      default: '',
    },
    selectedConfig: { // 配置文件入口，单个配置
      type: Object,
      default: null,
    },
    scopeData: { // 进程管理入口，多个配置
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      curStep: 1,
      steps: [
        { title: this.$t('选择实例'), icon: 1 },
        { title: this.$t('配置生成'), icon: 2 },
      ],

      isDropdownMode: true, // 筛选表达式模式，true 下拉 false 输入
      selectedScope: null, // 筛选表达式查询条件
      selectedChanged: true, // 到第二步时是否要自动 重新生成配置
      isMultipleTemplates: Boolean(!this.selectedConfig), // 从进程管理页面进来有多个配置模板
      totalTemplates: [], // 配置模板列表（不包含没有版本的模板）
      validTemplates: [], // 配置模板列表（过滤掉没查到实例列表的模板）
      selectedTemplateIds: [], // 选中的配置模板 id 列表
      selectedTemplates: [], // 选中的配置模板
      instanceTotalList: {}, // 所有模板 id 对应的实例列表
      instanceTotalVersion: {}, // 所有模板 id 对应的选中版本
      validTableRefs: [], // 有列表的表格组件实例

      fakeLoading: false, // 组件过渡 loading
      basicLoading: false, // 组件主体 loading
      retryLoading: false, // 全部重试按钮 loading
      generateLoading: false, // 下一步、全部重新生成按钮 loading
      generateFailureLoading: false, // 重试失败项按钮 loading
      distributeLoading: false, // 配置下发按钮 loading

      canNextStep: false, // 所有表格有数据才可以进行下一步
      isTasking: false, // 是否有配置正在生成或下发
      isAllGeneratedSuccess: false, // 是否所有配置生成成功
    };
  },
  computed: {
    isConfigCheck() {
      return this.action === 'configCheck';
    },
    maxHeight() {
      return this.isConfigCheck ? this.$store.state.pageHeight - 317 : 464;
    },
  },
  watch: {
    curStep(val) {
      if (val === 2) {
        this.fakeLoading = true;
        setTimeout(() => {
          this.fakeLoading = false;
        }, 400);
      }
    },
  },
  created() {
    if (!this.selectedConfig) {
      this.isDropdownMode = this.scopeData.isDropdownMode;
      this.selectedScope = this.scopeData.selectedScope;
    }
  },
  mounted() {
    // second init
    this.initPage();
  },
  methods: {
    // first init
    initSelectData(isDropdownMode, selectedScope) {
      this.isDropdownMode = isDropdownMode;
      this.selectedScope = selectedScope;
    },
    // 初始化，获取模板列表
    async initPage() {
      if (this.selectedConfig) {
        // 配置文件入口，单个配置
        this.totalTemplates = [this.selectedConfig];
        await this.initTotalList();
      } else {
        // 进程管理入口，多个配置
        // 回填数据
        const options = { silent: true };
        if (!this.isDropdownMode) {
          this.$refs.selectInstanceRef.setExpressionValue(this.selectedScope, options);
        }
        try {
          const res = await this.$store.dispatch('configTemplate/ajaxGetConfigTemplateList', { pagesize: 1000 });
          this.totalTemplates = res.data.list.filter(item => item.has_version);
          await this.initTotalList();
        } catch (e) {
          console.warn(e);
        }
      }
    },
    // 初始化模板对应的列表数据，初始化可用模板列表
    async initTotalList() {
      this.instanceTotalList = {};
      this.validTemplates = [];
      this.selectedTemplateIds = [];
      this.selectedTemplates = [];
      this.canNextStep = false;
      this.fetchAllInstanceList();
    },
    // 下一步的时候需要重新拉取 filter_released 未false 拿到的请求结果用作表格数据
    // 可能还会带有 版本筛选 条件在里边
    async fetchAllInstanceList() {
      return new Promise(async (resolve) => {
        try {
          this.basicLoading = true;
          const templateIds = this.selectedTemplateIds.length
            ? this.totalTemplates.filter(item => this.selectedTemplateIds.includes(item.config_template_id))
            : this.totalTemplates;

          const promiseList = templateIds.map(item => this.fetchInstanceList(item));
          const res = await Promise.all(promiseList);
          if (this.isMultipleTemplates) {
            const instanceTotalList = {};
            const validTemplates = [];
            const selectedTemplateIds = [];
            res.forEach((item) => {
              const [templateId, template, list] = item;
              if (this.curStep === 2 || list.length) {
                // 过滤掉没有数据的表格
                instanceTotalList[templateId] = list;
                validTemplates.push(template);
                selectedTemplateIds.push(templateId);
              }
            });
            this.instanceTotalList = instanceTotalList;
            this.validTemplates = validTemplates;
            this.selectedTemplateIds = selectedTemplateIds;
            // 这里下拉组件会自动执行
            // this.selectedTemplates = [...validTemplates]
            // this.canNextStep = selectedTemplateIds.length !== 0
            if (this.curStep === 1) {
              if (this.totalTemplates.length !== validTemplates.length) {
                this.messageInfo(this.$t('已匹配当前进程范围下所有配置文件'));
              }
            } else {
              this.selectedTemplates = [...validTemplates];
            }
          } else {
            const [templateId, template, list] = res[0];
            this.instanceTotalList = { [templateId]: list };
            this.validTemplates = [template];
            this.selectedTemplateIds = [templateId];
            this.selectedTemplates = [template];
            this.canNextStep = list.length !== 0;
          }
          this.basicLoading = false;
          resolve(res);
        } catch (e) {
          // 重复请求导致被 cancel
          console.warn(e);
          resolve(false);
        }
      });
    },
    fetchInstanceList(template) {
      const templateId = template.config_template_id;
      return new Promise(async (resolve, reject) => {
        try {
          const data = {
            [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
            config_template_id: templateId,
            filter_released: this.curStep === 1, // 实例的item.config_version_id版本显示的是下发的版本，而不是生成的版本
          };
          if (this.instanceTotalVersion[templateId]) {
            data.config_version_ids = this.instanceTotalVersion[templateId];
          }
          const res = await this.$store.dispatch('configInstance/ajaxGetConfigInstanceList', { data });
          resolve([templateId, template, res.data]);
        } catch (e) {
          console.warn(e);
          if (e.message === 'request canceled: post_/api/3/config_instance/list_config_instances/') {
            reject(new Error('实例列表请求被取消'));
          } else {
            resolve([templateId, template, []]);
          }
        }
      });
    },
    // 选择配置模板
    handleSelectTemplate(ids) {
      this.selectedTemplates = ids.map(id => this.validTemplates.find(item => item.config_template_id === id));
      this.canNextStep = ids.length !== 0;
    },

    // 进程范围筛选值改变，所有表格重新查询配置实例列表（重新渲染）
    handleSelectInstance(isDropdownMode, selectedScope) {
      this.selectedChanged = true;
      this.isDropdownMode = isDropdownMode;
      this.selectedScope = selectedScope;
      this.initTotalList();
    },
    // 全部重新生成
    async handleGenerateAll() {
      this.isTasking = true;
      this.generateLoading = true;
      this.isAllGeneratedSuccess = false;
      const promiseList = this.validTableRefs.map(vm => vm.generateConfig({ isFirstStep: false }));
      const result = await Promise.all(promiseList);
      this.isTasking = false;
      this.generateLoading = false;
      this.isAllGeneratedSuccess = result.every(Boolean);
      this.selectedChanged = false;
    },
    // 重试失败项
    async handleGenerateFailure() {
      this.isTasking = true;
      this.generateFailureLoading = true;
      this.isAllGeneratedSuccess = false;
      const promiseList = this.validTableRefs.map(vm => vm.generateFailure());
      const result = await Promise.all(promiseList);
      this.isTasking = false;
      this.generateFailureLoading = false;
      this.isAllGeneratedSuccess = result.every(Boolean);
    },

    // 下一步
    async handleNext() {
      this.curStep += 1;
      this.isTasking = true;
      this.isAllGeneratedSuccess = false;
      await this.fetchAllInstanceList();
      const validTableRefs = [];
      this.selectedTemplateIds.forEach((id) => {
        const componentInstance = this.$refs[`tableRef_${id}`][0];
        if (componentInstance.filterInstanceList.length > 0) {
          componentInstance.initTableData();
          validTableRefs.push(componentInstance);
        }
      });
      this.validTableRefs = validTableRefs;
      const promiseList = this.validTableRefs.map(vm => vm.generateConfig({ isFirstStep: true }));
      const result = await Promise.all(promiseList);
      this.isTasking = false;
      this.isAllGeneratedSuccess = result.every(Boolean);
      if (this.selectedChanged) {
        this.handleGenerateAll();
      }
    },
    // 配置下发
    async handleDistribute() {
      this.isTasking = true;
      this.distributeLoading = true;
      if (this.isConfigCheck) {
        const validTableRefs = [];
        this.selectedTemplateIds.forEach((id) => {
          const componentInstance = this.$refs[`tableRef_${id}`][0];
          if (componentInstance.filterInstanceList.length > 0) {
            componentInstance.initTableData();
            validTableRefs.push(componentInstance);
          }
        });
        this.validTableRefs = validTableRefs;
      }
      const promiseList = this.validTableRefs.map(vm => vm.distributeConfig());
      const result = await Promise.all(promiseList);
      if (result.length === 1) {
        // 单个任务
        const { jobId } = result[0];
        if (jobId) {
          // 成功，跳转到任务历史详情
          this.$store.commit('routeTaskHistoryDetail', jobId);
        } else {
          // 失败，停留在当前页面
          this.isTasking = false;
          this.distributeLoading = false;
        }
      } else {
        // 多个任务，无论成功失败直接跳转到任务历史列表
        this.messageInfo(this.$t('配置下发拆分为多个子任务，请关注最终执行结果'));
        const ids = result.map(item => item.jobId).filter(Boolean)
          .join(',');
        this.$store.commit('routeTaskHistoryList', ids);
      }
    },
    // 上一步
    handlePrevious() {
      this.curStep -= 1;
      this.instanceTotalVersion = {};
      // 这里重新拉取实例列表，以获取最新配置状态
      // 比如开始是 not_latest，后面生成后变成了 generated 还是 not_generated
      // 前端是不知道的，因为没有根据任务状态去修改配置状态的属性
      this.validTableRefs = [];
      this.initTotalList();
    },
    // 取消
    handleCancel() {
      if (this.$router.__from_name) {
        this.$router.back();
      } else {
        this.$store.commit('routeConfigTemplateList');
      }
    },
    // 更新table选中version
    updateInstanceVersion(version) {
      Object.assign(this.instanceTotalVersion, version);
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../css/variable.css';
  @import '../../css/mixins/scroll.css';

  .config-file-template-distribute-container {
    display: flex;
    flex-flow: column;
    height: 100%;
    position: relative;
    background-color: #f5f6fa;

    .distribute-above {
      flex-shrink: 0;
      padding-bottom: 20px;

      /* 配置下发的步骤组件 */
      .steps-container {
        display: flex;
        justify-content: center;
        height: 40px;
        margin: 0 auto;
        background-color: #f5f6fa;

        .king-steps {
          width: 372px;

          /deep/ .bk-step.current .bk-step-title {
            color: $newBlackColor1;
          }
        }
      }

      .form-container {
        display: flex;
        align-items: center;
        padding: 20px 60px 0;
        color: #63656e;
        font-size: 14px;

        .star-title {
          flex-shrink: 0;
          width: 80px;

          &:after {
            margin-left: 4px;
            content: '*';
            color: #ea3636;
          }
        }

        .select-instance-container {
          padding-left: 0;
          height: auto;
        }

        .king-select {
          width: 955px;
          background-color: #fff;
        }
      }

      .buttons-above {
        display: flex;
        align-items: center;
        padding: 20px 60px 0;
      }
    }

    .distribute-below {
      height: 100%;
      overflow: auto;

      @mixin scroller;

      .buttons-below {
        position: sticky;
        z-index: 10;
        bottom: 0;
        display: flex;
        justify-content: center;
        height: 72px;
        padding-top: 20px;
        background-color: #f5f6fa;
      }
    }
  }
</style>
