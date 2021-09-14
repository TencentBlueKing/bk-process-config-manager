<template>
  <div v-if="isEmptyTopo" class="empty-topo-container">
    <img src="../../../../../assets/images/empty-topo.png" width="240" alt="">
    <div class="empty-title">{{ $t('暂无业务拓扑') }}</div>
    <i18n path="无拓扑提示">
      <slot>
        <bk-button text theme="primary" class="reset-icon-btn" @click="jumpToConfigPlatform">
          {{ $t('配置平台') }}<i class="gsekit-icon gsekit-icon-jump-fill"></i>
        </bk-button>
      </slot>
    </i18n>
    <bk-button class="king-button-init" :loading="isLoading" @click="init">{{ $t('刷新') }}</bk-button>
  </div>
  <div v-else class="process-select-container">
    <div class="bind-process">
      <div class="block-title">{{ $t('选择关联进程') }}</div>
      <div class="bk-button-group">
        <bk-button :class="['king-button', showTemp && 'is-selected']" @click="activeTab = 'service-temp'">
          {{ $t('按服务模板') }}
        </bk-button>
        <bk-button :class="['king-button', showTopo && 'is-selected']" @click="activeTab = 'biz-topo'">
          {{ $t('按业务拓扑') }}
        </bk-button>
      </div>
      <!-- 业务拓扑搜索框 -->
      <bk-input
        v-show="showTopo"
        v-model.trim="topoSearchKeyword"
        :clearable="true"
        class="king-input"
        right-icon="icon-search"
        @change="handleSearch('topoData', $event)"
      ></bk-input>
      <!-- 服务模板搜索框 -->
      <bk-input
        v-show="showTemp"
        v-model.trim="tempSearchKeyword"
        :clearable="true"
        class="king-input"
        right-icon="icon-search"
        @change="handleSearch('templateList', $event)"
      ></bk-input>
      <div class="scroll-container" v-bkloading="{ isLoading }">
        <TopoTree
          v-show="showTopo"
          :template-process.sync="templateProcess"
          :instance-process.sync="instanceProcess"
          :node-list="topoData"
          @checked="handleCheckNode" />
        <div v-if="isEmptyService" v-show="showTemp" class="empty-service-container">
          <EmptyServiceBox type="template" />
          <bk-button
            class="king-button-refresh-service"
            :loading="emptyServiceLoading"
            @click="refreshService">
            {{ $t('刷新') }}
          </bk-button>
        </div>
        <TopoTree
          v-else
          v-show="showTemp"
          :node-list="templateList"
          :template-process.sync="templateProcess"
          :instance-process.sync="instanceProcess"
          @checked="handleCheckNode" />
      </div>
    </div>
    <div class="result-preview">
      <div class="block-title">{{ $t('结果预览') }}</div>
      <div class="scroll-container">
        <!-- 模板进程 -->
        <div class="process-list-container">
          <div class="title" @click="showTemplateProcess = !showTemplateProcess">
            <span class="bk-icon icon-right-shape" :class="showTemplateProcess && 'expanded'"></span>
            {{ $t('已选') }}
            <span class="process-length">{{ templateProcess.length }}</span>
            {{ $t('个模板进程') }}
          </div>
          <!-- 模板进程列表 -->
          <ul class="process-list" v-show="showTemplateProcess">
            <template v-for="(item, index) in templateProcess">
              <li class="process-item" :key="index + Date.now()">
                <div class="white-card">
                  <div v-bk-overflow-tips class="white-card-left">{{ item.topoName }}</div>
                  <div class="white-card-right">
                    <span class="gsekit-icon gsekit-icon-parenet-node-line"></span>
                    {{ item.topoTemplateName }}
                  </div>
                </div>
                <div class="close-icon-container">
                  <span class="bk-icon icon-close" @click="removeTemplateProcess(item, index)"></span>
                </div>
              </li>
            </template>
          </ul>
        </div>
        <!-- 实例进程 -->
        <div class="process-list-container">
          <div class="title" @click="showInstanceProcess = !showInstanceProcess">
            <span class="bk-icon icon-right-shape" :class="showInstanceProcess && 'expanded'"></span>
            {{ $t('已选') }}
            <span class="process-length">{{ instanceProcess.length }}</span>
            {{ $t('个实例进程') }}
          </div>
          <!-- 实例进程列表 -->
          <ul class="process-list" v-show="showInstanceProcess">
            <template v-for="(item, index) in instanceProcess">
              <li class="process-item" :key="index + Date.now()">
                <div class="white-card">
                  <div v-bk-overflow-tips class="white-card-left">{{ item.topoName }}</div>
                  <div class="white-card-right" v-bk-tooltips.bottom="item.topoReduceName">
                    <span class="gsekit-icon gsekit-icon-parenet-node-line"></span>
                    {{ item.topoParent.topoName }}
                  </div>
                </div>
                <div class="close-icon-container">
                  <span class="bk-icon icon-close" @click="removeInstanceProcess(item, index)"></span>
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
import TopoTree from './TopoTree';
import EmptyServiceBox from '@/components/Empty/EmptyServiceBox';
import { sortByCustom } from '@/common/util';

export default {
  components: {
    TopoTree,
    EmptyServiceBox,
  },
  props: {
    // 是否需要回填已绑定的关系
    shouldBackfill: {
      type: Boolean,
      default: false,
    },
    // 当前绑定的配置模板
    templateId: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      activeTab: 'service-temp', // biz-topo 业务拓扑 service-temp 服务模板
      topoSearchKeyword: '', // topo 搜索内容
      tempSearchKeyword: '', // 服务模板搜索内容
      searchTimer: null,
      isLoading: false,
      isEmptyTopo: false,
      isEmptyService: false,
      emptyServiceLoading: false,
      topoData: [], // 业务拓扑节点列表
      templateList: [], // 服务模板列表
      templateProcess: [], // 模板进程
      showTemplateProcess: true,
      instanceProcess: [], // 实例进程
      showInstanceProcess: true,
    };
  },
  computed: {
    showTopo() {
      return this.activeTab === 'biz-topo';
    },
    showTemp() {
      return this.activeTab === 'service-temp';
    },
  },
  created() {
    this.init();
  },
  methods: {
    // 获取topo树和服务模板列表，接口获取的服务模板列表数据不同于topo树里面的服务模板
    async init() {
      try {
        this.isLoading = true;
        const [topoRes, templateRes, relationRes] = await Promise.all([
          this.$store.dispatch('cmdb/ajaxGetBizTopo'),
          this.$store.dispatch('cmdb/ajaxGetServiceTemplate'),
          this.shouldBackfill
            ? this.$store.dispatch('configTemplate/ajaxGetTemplateBindRelationship', { templateId: this.templateId })
            : Promise.resolve(null),
        ]);
        // 处理topo树数据
        const topoData = topoRes.data.length ? topoRes.data[0].child : [];
        if (!topoData.length) {
          this.isEmptyTopo = true;
          return;
        }
        this.filterTopoData(topoData);
        this.topoData = topoData;
        // 处理服务模板数据
        this.isEmptyService = !templateRes.data.length;
        this.filterTemplateData(templateRes.data);
        this.templateList = templateRes.data;
        // 绑定关系回填
        relationRes && this.recoverBindRelationship(relationRes.data);
      } catch (e) {
        console.warn(e);
        this.isEmptyTopo = true;
      } finally {
        this.isLoading = false;
      }
    },
    // 遍历拓扑树，结构如下：
    // set
    // set module
    // set module (serviceInstance)
    // set serviceTemplate
    // 集群
    // 集群 模块
    // 集群 模块 (服务实例)
    // 集群 服务模板
    filterTopoData(topoData, topoLevel = -1, parent = null) {
      topoLevel += 1;
      topoData.sort(sortByCustom('bk_inst_name'));
      topoData.forEach((item) => {
        item.topoParent = parent;
        item.topoVisible = true;
        item.topoExpand = false;
        item.topoLoading = false;
        item.topoLevel = topoLevel;
        item.topoName = item.bk_inst_name;
        item.topoProcessCount = item.process_count;
        item.topoReduceName = parent ? `${parent.topoReduceName}/${item.topoName}` : item.topoName;
        item.topoProcess = false;
        if (item.bk_obj_id === 'set') {
          item.topoType = 'set'; // 集群
        } else if (item.bk_obj_id === 'module') {
          if (item.service_template_id) { // 服务模板（下面是模板进程）
            item.topoType = 'serviceTemplate';
          } else { // 模块（下面是实例，实例下面是实例进程）
            item.topoType = 'module';
          }
        }
        if (item.child && item.child.length) {
          this.filterTopoData(item.child, topoLevel, item);
        }
      });
    },
    // 处理服务模板列表数据
    filterTemplateData(templateData) {
      templateData.sort(sortByCustom('name'));
      templateData.forEach((item) => {
        item.child = [];
        item.topoParent = null;
        item.topoVisible = true;
        item.topoExpand = false;
        item.topoLoading = false;
        item.topoLevel = 0;
        item.topoName = item.name;
        item.topoProcess = false;
        item.topoType = 'serviceTemplate';
      });
    },
    // 绑定关系回填
    recoverBindRelationship(processList) {
      try {
        const templateProcess = [];
        const instanceProcess = [];
        processList.forEach((item) => {
          const info = item.process_obj_info;
          if (item.process_object_type === 'TEMPLATE') {
            templateProcess.push({
              __IS_RECOVER: true,
              id: item.process_object_id,
              topoName: info.process_object_name,
              topoTemplateName: info.service_template_name,
            });
          } else if (item.process_object_type === 'INSTANCE') {
            instanceProcess.push({
              __IS_RECOVER: true,
              property: {
                bk_process_id: item.process_object_id,
              },
              topoName: info.bk_process_name,
              topoReduceName: `${info.bk_set_name}/${info.bk_module_name}/${info.bk_service_name}`,
              topoParent: {
                topoName: info.bk_service_name,
              },
            });
          }
        });
        this.templateProcess = templateProcess;
        this.instanceProcess = instanceProcess;
      } catch (e) {
        console.warn('绑定关系回填失败', e);
      }
    },
    // 当前业务暂无服务模板，刷新
    async refreshService() {
      try {
        this.emptyServiceLoading = true;
        const res = await this.$store.dispatch('cmdb/ajaxGetServiceTemplate');
        this.isEmptyService = !res.data.length;
        this.filterTemplateData(res.data);
        this.templateList = res.data;
      } catch (e) {
        console.warn(e);
      } finally {
        this.emptyServiceLoading = false;
      }
    },

    // 搜索树节点
    handleSearch(treeData, keyword) {
      this.isLoading = true;
      this.searchTimer && clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        const list = this[treeData];
        this.searchTree(list, keyword);
        this.isLoading = false;
      }, 300);
    },
    searchTree(list, keyword) {
      list.forEach((item) => {
        item.topoExpand = false;
        const isMatched = item.topoName.includes(keyword);
        item.topoVisible = isMatched;
        if (isMatched) {
          this.setParentVisible(item.topoParent, keyword);
        }
        if (item.child && item.child.length) {
          this.searchTree(item.child, keyword);
        }
      });
    },
    setParentVisible(node, keyword) {
      if (node) {
        node.topoVisible = true;
        node.topoExpand = Boolean(keyword);
        this.setParentVisible(node.topoParent, keyword);
      }
    },

    // 选择进程节点
    handleCheckNode(topoNode) {
      if (topoNode.topoType === 'templateProcess') {
        if (topoNode.topoChecked) { // 选择进程
          const { templateProcess } = this;
          // 查看已选择的模板进程是否包含当前进程（业务拓扑、服务模板两棵树有重复的进程）
          let findItem; let findIndex;
          for (let i = 0; i < templateProcess.length; i++) {
            const item = templateProcess[i];
            if (item.id === topoNode.id) {
              findItem = item;
              findIndex = i;
              break;
            }
          }
          if (findItem) {
            findItem.topoChecked = false;
            templateProcess.splice(findIndex, 1, topoNode);
          } else {
            this.templateProcess.push(topoNode);
          }
        } else { // 取消选择
          const index = this.templateProcess.findIndex(item => item === topoNode);
          this.templateProcess.splice(index, 1);
        }
      } else if (topoNode.topoType === 'instanceProcess') {
        if (topoNode.topoChecked) { // 选择进程
          this.instanceProcess.push(topoNode);
        } else { // 取消选择
          const index = this.instanceProcess.findIndex(item => item === topoNode);
          this.instanceProcess.splice(index, 1);
        }
      }
    },

    // 移除模板进程
    removeTemplateProcess(item, index) {
      item.topoChecked = false;
      this.templateProcess.splice(index, 1);
    },
    // 移除实例进程
    removeInstanceProcess(item, index) {
      item.topoChecked = false;
      this.instanceProcess.splice(index, 1);
    },

    jumpToConfigPlatform() {
      const { bizId } = this.$store.state;
      window.open(`${window.PROJECT_CONFIG.CMDB_URL}/#/business/${bizId}/index?node=biz-${bizId}`, '_blank');
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';
  @import '../../../../../css/mixins/scroll.css';

  .empty-topo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    height: 502px;
    font-size: 13px;
    line-height: 18px;
    color: $newBlackColor3;

    .empty-title {
      margin: 20px 0 16px;
      font-size: 16px;
      text-align: left;
      line-height: 20px;
      color: $newBlackColor2;
    }

    .king-button-init {
      width: 86px;
      margin: 16px 0;
    }
  }

  .process-select-container {
    display: flex;
    height: 502px;

    .block-title {
      font-size: 16px;
      line-height: 20px;
      color: #313238;
    }

    .bind-process {
      width: 524px;
      padding: 20px 24px;

      .bk-button-group {
        width: 100%;
        padding: 14px 0 12px;

        .king-button {
          width: 50%;
        }
      }

      .king-input {
        margin-bottom: 12px;
      }

      .scroll-container {
        height: calc(100% - 122px);
        overflow: auto;

        @mixin scroller;

        .empty-service-container {
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
          flex-direction: column;

          >>> .empty-service-box {
            flex: 0;
            height: auto;
          }

          .king-button-refresh-service {
            width: 86px;
            margin: 0 0 16px;
          }
        }
      }
    }

    .result-preview {
      width: calc(100% - 524px);
      padding: 20px 24px;
      background-color: #f5f6fa;

      .scroll-container {
        height: calc(100% - 20px);
        overflow: auto;

        @mixin scroller;

        .process-list-container {
          margin-top: 15px;

          .title {
            display: flex;
            align-items: center;
            height: 30px;
            line-height: 20px;
            margin-bottom: 5px;
            color: $newBlackColor2;
            font-size: 14px;
            cursor: pointer;
            transition: background-color .3s;

            &:hover {
              background-color: #f0f1f5;
              transition: background-color .3s;
            }

            .icon-right-shape {
              margin-right: 4px;
              color: #c4c6cc;
              transition: transform .3s;

              &.expanded {
                transform: rotate(90deg);
                transition: transform .3s;
              }
            }

            .process-length {
              color: $newMainColor;
              font-weight: bold;
              padding: 0 4px;
            }
          }

          .process-list {
            .process-item {
              display: flex;

              &:not(:last-child) {
                margin-bottom: 2px;
              }

              .white-card {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: calc(100% - 28px);
                height: 32px;
                line-height: 16px;
                padding: 0 18px;
                background-color: #fff;
                border-radius: 2px;
                box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .06);

                .white-card-left {
                  width: 100%;
                  height: 18px;
                  margin-top: 1px;
                  overflow: hidden;
                  white-space: nowrap;
                  text-overflow: ellipsis;
                }

                .white-card-right {
                  flex-shrink: 0;
                  display: flex;
                  align-items: center;
                  margin-left: 12px;
                  font-size: 12px;
                  color: $newBlackColor3;

                  .gsekit-icon-parenet-node-line {
                    margin-right: 4px;
                    font-size: 16px;
                  }
                }
              }

              .close-icon-container {
                display: flex;
                align-items: center;
                width: 28px;
                padding-left: 8px;

                .icon-close {
                  font-size: 20px;
                  color: #c4c6cc;
                  cursor: pointer;

                  &:hover {
                    color: $newMainColor;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
</style>
