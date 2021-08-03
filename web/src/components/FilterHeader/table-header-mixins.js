import FilterHeader from '@/components/FilterHeader';

export default {
  data() {
    return {
      filterData: [],
      // search select绑定值
      searchSelectValue: [],
      // search select数据源
      searchSelectData: [],
      // 判断数据列表是否展示
      isMenuShow: false,
    };
  },
  computed: {
    headerData() { // 表头筛选列表数据源
      return this.filterData.reduce((obj, item) => {
        if (item.children && item.children.length) {
          obj[item.id] = item.children;
        }
        return obj;
      }, {});
    },
  },
  watch: {
    searchSelectValue: {
      handler() {
        this.handleSearchSelectFilter();
        this.handlePageChange(1);
      },
      deep: true,
    },
  },
  methods: {
    // 自定筛选表头
    renderFilterHeader(h, data) {
      const filterList = this.headerData[data.column.property] || [];
      this.setChecked(filterList);
      const title = data.column.label || '';
      const property = data.column.property || '';
      return <FilterHeader
                name={ title } property={ property } filterList={ filterList }
                onConfirm={ (prop, list) => this.handleFilterHeaderConfirm(prop, list) }
                onReset={ prop => this.handleFilterHeaderReset(prop) }>
            </FilterHeader>;
    },
    setChecked(data) {
      data.forEach((item) => {
        if (!item.checked) {
          item.checked = false;
        }
        for (const { id, values } of this.searchSelectValue) {
          const createdId = values.map(item => item.id);
          if (id === 'created_by' && createdId.includes(item.id)) {
            item.checked = true;
            return;
          }
        }
        if (item.child && item.child.length) {
          this.setChecked(item.child);
        }
      });
    },
    // 处理search select的过滤数据
    handleSearchSelectFilter() {
      const filterData = this.filterData.filter((item) => {
        for (const { id } of this.searchSelectValue) {
          if (item.id === id) {
            return false;
          }
        }
        return true;
      });
      if (!filterData.length && this.isMenuShow) {
        this.$refs.searchSelect.popperMenuInstance.hide();
      }
      this.searchSelectData = filterData;
    },
    handleSearchSelectShowMenu() {
      this.isMenuShow = true;
    },
    /**
         * search select输入框信息变更
         */
    handleSearchSelectChange(list) {
      this.filterData.forEach((data) => {
        const item = list.find(item => item.id === data.id);
        if (data.children) {
          data.children = data.children.map((child) => {
            if (!item) {
              child.checked = false;
            } else {
              child.checked = item.values.some(value => value.id === child.id);
            }
            return child;
          });
        }
      });
    },
    handleFilterHeaderReset(prop) {
      const index = this.searchSelectValue.findIndex(item => item.id === prop);
      if (index > -1) {
        this.searchSelectValue.splice(index, 1);
      }
    },
    // 表头筛选变更
    handleFilterHeaderConfirm(prop, list) {
      this.isMenuShow = false;
      const index = this.searchSelectValue.findIndex(item => item.id === prop);
      const values = list.reduce((pre, item) => {
        if (item.checked) {
          pre.push({
            id: item.id,
            name: item.name,
          });
        }
        return pre;
      }, []);
      if (index > -1) {
        // 已经存在就覆盖
        this.searchSelectValue[index].values = values;
      } else {
        const data = this.filterData.find(data => data.id === prop);
        // 不存在就添加
        this.searchSelectValue.push({
          id: prop,
          name: data ? data.name : '',
          values,
        });
      }
    },
  },
};
