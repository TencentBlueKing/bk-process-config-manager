(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[8],{221:function(e,t,a){"use strict";a.r(t);var r=function(){var e=this;var t=e.$createElement;var a=e._self._c||t;return a("div",{directives:[{name:"test",rawName:"v-test",value:"configFile",expression:"'configFile'"}],staticClass:"config-file-template-list-container"},[a("div",{staticClass:"title"},[e._v(e._s(e.$t("配置文件模板")))]),e._v(" "),a("div",{staticClass:"option-group"},[a("AuthTag",{directives:[{name:"test",rawName:"v-test",value:"addTemp",expression:"'addTemp'"}],attrs:{action:"create_config_template",authorized:e.authMap.create_config_template},scopedSlots:e._u([{key:"default",fn:function(t){var r=t.disabled;return[a("bk-button",{staticClass:"king-button",attrs:{theme:"primary",disabled:r},on:{click:function(t){e.showCreate=true}}},[e._v("\n          "+e._s(e.$t("新建"))+"\n        ")])]}}])}),e._v(" "),a("bk-input",{directives:[{name:"test",rawName:"v-test",value:"searchTemp",expression:"'searchTemp'"}],staticClass:"king-input",attrs:{placeholder:e.$t("请输入文件名或模板名"),"right-icon":"icon-search",clearable:""},on:{enter:e.handleSearch,blur:e.handleSearch,clear:e.handleSearch},model:{value:e.searchWord,callback:function(t){e.searchWord=typeof t==="string"?t.trim():t},expression:"searchWord"}})],1),e._v(" "),a("bk-table",{directives:[{name:"bkloading",rawName:"v-bkloading",value:{isLoading:e.templateLoading,zIndex:0},expression:"{ isLoading: templateLoading, zIndex: 0 }"}],staticClass:"king-table",attrs:{"auto-scroll-to-top":"","max-height":e.$store.state.pageHeight-190,data:e.templateList,pagination:e.pagination},on:{"sort-change":e.handleSortChange,"page-change":e.handlePageChange,"page-limit-change":e.handlePageLimitChange}},[a("bk-table-column",{attrs:{label:e.$t("模板名称"),prop:"template_name",sortable:"custom"},scopedSlots:e._u([{key:"default",fn:function(t){var r=t.row;return a("div",{staticClass:"template-name-column"},[a("AuthTag",{directives:[{name:"bk-overflow-tips",rawName:"v-bk-overflow-tips"},{name:"test",rawName:"v-test",value:"viewTemp",expression:"'viewTemp'"}],staticClass:"button-text",attrs:{action:"edit_config_template",id:r.config_template_id,authorized:r.edit_config_template},on:{click:function(t){e.operateVersionList(r)}}},[e._v("\n          "+e._s(r.template_name)+"\n        ")]),e._v(" "),!r.has_version?a("span",{directives:[{name:"bk-tooltips",rawName:"v-bk-tooltips",value:e.$t("没有可用版本，无法进行配置下发"),expression:"$t('没有可用版本，无法进行配置下发')"}],staticClass:"gsekit-icon gsekit-icon-alert"}):e._e()],1)}}])}),e._v(" "),a("bk-table-column",{attrs:{label:e.$t("文件名"),prop:"file_name",sortable:"custom"},scopedSlots:e._u([{key:"default",fn:function(t){var r=t.row;return a("div",{directives:[{name:"bk-overflow-tips",rawName:"v-bk-overflow-tips"}],staticClass:"table-ceil-overflow"},[a("span",[e._v(e._s(r.file_name))])])}}])}),e._v(" "),a("bk-table-column",{attrs:{label:e.$t("文件所处路径"),prop:"abs_path",sortable:"custom"},scopedSlots:e._u([{key:"default",fn:function(t){var r=t.row;return a("div",{directives:[{name:"bk-overflow-tips",rawName:"v-bk-overflow-tips"}],staticClass:"table-ceil-overflow"},[a("span",[e._v(e._s(r.abs_path))])])}}])}),e._v(" "),a("bk-table-column",{attrs:{label:e.$t("关联进程数")},scopedSlots:e._u([{key:"default",fn:function(t){var r=t.row;return[r.is_bound?a("bk-popover",{attrs:{placement:"right"}},[a("div",{directives:[{name:"test",rawName:"v-test",value:"numConnect",expression:"'numConnect'"}],staticClass:"button-text",staticStyle:{"min-width":"20px","line-height":"28px"},on:{click:function(t){e.operateBind(r)}}},[e._v("\n            "+e._s(r.relation_count.TEMPLATE+r.relation_count.INSTANCE)+"\n          ")]),e._v(" "),a("div",{attrs:{slot:"content"},slot:"content"},[a("div",[e._v(e._s("模板进程："+r.relation_count.TEMPLATE))]),e._v(" "),a("div",[e._v(e._s("实例进程："+r.relation_count.INSTANCE))])])]):a("div",{directives:[{name:"bk-tooltips",rawName:"v-bk-tooltips",value:e.$t("未关联进程，无法进行配置下发，点击关联"),expression:"$t('未关联进程，无法进行配置下发，点击关联')"},{name:"test",rawName:"v-test",value:"numConnect",expression:"'numConnect'"}],staticClass:"not-bound-column",on:{click:function(t){e.operateBind(r)}}},[a("span",[e._v(e._s(e.$t("未关联")))]),e._v(" "),a("span",{staticClass:"gsekit-icon gsekit-icon-alert"})])]}}])}),e._v(" "),a("bk-table-column",{attrs:{label:e.$t("更新人"),prop:"updated_by",filters:e.updatePersonFilters,"filter-method":e.commonFilterMethod,"filter-multiple":true}}),e._v(" "),a("bk-table-column",{attrs:{label:e.$t("更新时间"),prop:"updated_at",sortable:"custom"},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v("\n        "+e._s(e.formatDate(a.updated_at))+"\n      ")]}}])}),e._v(" "),a("bk-table-column",{attrs:{label:e.$t("操作")},scopedSlots:e._u([{key:"default",fn:function(t){var r=t.row;return a("div",{staticClass:"table-operation-container"},[a("AuthTag",{staticStyle:{"margin-right":"12px"},attrs:{action:"operate_config",authorized:e.authMap.operate_config},scopedSlots:e._u([{key:"default",fn:function(t){var n=t.disabled;return a("div",{directives:[{name:"bk-tooltips",rawName:"v-bk-tooltips",value:{content:!r.has_version?e.$t("没有可用版本，无法进行配置下发"):e.$t("未关联进程，无法进行配置下发"),disabled:r.has_version&&r.is_bound},expression:"{\n            content: !row.has_version ? $t('没有可用版本，无法进行配置下发') : $t('未关联进程，无法进行配置下发'),\n            disabled: row.has_version && row.is_bound\n          }"}]},[a("bk-button",{directives:[{name:"test",rawName:"v-test",value:"release",expression:"'release'"}],attrs:{text:"",theme:"primary",disabled:n||!r.has_version||!r.is_bound},on:{click:function(t){e.operateDistribute(r)}}},[e._v("\n              "+e._s(e.$t("配置下发"))+"\n            ")])],1)}}])}),e._v(" "),a("bk-button",{directives:[{name:"test",rawName:"v-test",value:"connectProcess",expression:"'connectProcess'"}],attrs:{theme:"primary",text:""},on:{click:function(t){e.operateBind(r)}}},[e._v("\n          "+e._s(e.$t("关联进程"))+"\n        ")]),e._v(" "),a("bk-popover",{attrs:{placement:"bottom-start",theme:"dot-menu light",trigger:"click",arrow:false,offset:"15",distance:0}},[a("div",{staticClass:"dot-menu-trigger"},[a("span",{directives:[{name:"test",rawName:"v-test.common",value:"more",expression:"'more'",modifiers:{common:true}}],staticClass:"bk-icon icon-more"})]),e._v(" "),a("ul",{staticClass:"dot-menu-list",attrs:{slot:"content"},slot:"content"},[a("AuthTag",{directives:[{name:"test",rawName:"v-test.common",value:"moreItem",expression:"'moreItem'",modifiers:{common:true}}],staticClass:"dot-menu-item",attrs:{tag:"li",action:"operate_config",authorized:e.authMap.operate_config},on:{click:function(t){e.operateGenerate(r)}}},[e._v("\n              "+e._s(e.$t("配置生成"))+"\n            ")]),e._v(" "),a("AuthTag",{directives:[{name:"test",rawName:"v-test.common",value:"moreItem",expression:"'moreItem'",modifiers:{common:true}}],staticClass:"dot-menu-item",attrs:{tag:"li",action:"delete_config_template",id:r.config_template_id,authorized:r.delete_config_template},on:{click:function(t){e.operateDelete(r)}}},[e._v("\n              "+e._s(e.$t("删除"))+"\n            ")])],1)])],1)}}])})],1),e._v(" "),a("CreateTemplateDialog",{attrs:{"show-create":e.showCreate},on:{"update:showCreate":function(t){e.showCreate=t},created:e.handleCreated}}),e._v(" "),a("BindProcessDialog",{attrs:{"template-item":e.templateItem,"show-dialog":e.showBindProcess},on:{"update:showDialog":function(t){e.showBindProcess=t},shouldRefreshList:e.getTemplateList}})],1)};var n=[];var i=a(3);var s=a.n(i);var o=a(13);var l=a.n(o);var c=a(11);var p=a.n(c);var u=a(7);var m=a.n(u);var d=a(4);var v=a.n(d);var f=a(8);var h=function(){var e=this;var t=e.$createElement;var a=e._self._c||t;return a("bk-dialog",{attrs:{value:e.showCreate,"mask-close":false,"close-icon":false,position:{top:e.dialogTop},width:"1000","ext-cls":"create-template-dialog","header-position":"left"},on:{"value-change":e.handleValueChange}},[a("div",{staticClass:"bk-dialog-header-inner",attrs:{slot:"header"},slot:"header"},[e.isFirstStep?[e._v("\n      "+e._s(e.$t("新建配置文件模板"))+"\n    ")]:[e._v("\n      "+e._s(e.$t("关联进程"))+"\n      "),a("span",{staticStyle:{"font-size":"14px","font-weight":"bold","line-height":"62px","vertical-align":"top"}},[e._v(e._s(" - "))]),e._v(" "),a("span",{staticStyle:{"font-size":"18px","font-weight":"normal"}},[e._v("\n        "+e._s(e.newTemplate.template_name+"("+e.newTemplate.file_name+")")+"\n      ")])]],2),e._v(" "),e.showCreate?[a("BasicInfo",{directives:[{name:"show",rawName:"v-show",value:e.isFirstStep,expression:"isFirstStep"}],ref:"basicInfo"}),e._v(" "),a("ProcessSelect",{directives:[{name:"show",rawName:"v-show",value:!e.isFirstStep,expression:"!isFirstStep"}],ref:"processSelect"})]:e._e(),e._v(" "),a("div",{staticClass:"footer-wrapper",attrs:{slot:"footer"},slot:"footer"},[a("bk-button",{directives:[{name:"show",rawName:"v-show",value:e.isFirstStep,expression:"isFirstStep"},{name:"test",rawName:"v-test.common",value:"stepNext",expression:"'stepNext'",modifiers:{common:true}}],attrs:{theme:"primary",loading:e.createLoading},on:{click:e.handleCreate}},[e._v("\n      "+e._s(e.$t("下一步"))+"\n    ")]),e._v(" "),a("bk-button",{directives:[{name:"show",rawName:"v-show",value:e.isFirstStep,expression:"isFirstStep"},{name:"test",rawName:"v-test.form",value:"cancel",expression:"'cancel'",modifiers:{form:true}}],on:{click:e.handleCancel}},[e._v("\n      "+e._s(e.$t("取消"))+"\n    ")]),e._v(" "),a("bk-button",{directives:[{name:"show",rawName:"v-show",value:!e.isFirstStep,expression:"!isFirstStep"},{name:"test",rawName:"v-test.form",value:"confirm",expression:"'confirm'",modifiers:{form:true}}],attrs:{theme:"primary",loading:e.bindLoading},on:{click:e.handleBind}},[e._v("\n      "+e._s(e.$t("关联"))+"\n    ")]),e._v(" "),a("bk-button",{directives:[{name:"show",rawName:"v-show",value:!e.isFirstStep,expression:"!isFirstStep"},{name:"test",rawName:"v-test.form",value:"cancel",expression:"'cancel'",modifiers:{form:true}}],on:{click:e.handleSkip}},[e._v("\n      "+e._s(e.$t("暂不关联"))+"\n    ")])],1)],2)};var g=[];var _=function(){var e=this;var t=e.$createElement;var a=e._self._c||t;return a("div",{staticClass:"create-template-step2"},[a("div",{staticClass:"title"},[e._v(e._s(e.$t("基本信息")))]),e._v(" "),a("bk-form",{directives:[{name:"test",rawName:"v-test",value:"tempForm",expression:"'tempForm'"}],ref:"form",staticClass:"king-form",attrs:{"label-width":350,model:e.formData,rules:e.rules}},[e._l(e.formItems,function(t){return[a("bk-form-item",{key:t.prop,attrs:{"error-display-type":"normal",label:t.label,required:t.required,property:t.prop}},[t.type==="select"?a("bk-select",{directives:[{name:"test",rawName:"v-test",value:"tempSelect",expression:"'tempSelect'"}],attrs:{"test-key":t.prop,clearable:true,placeholder:t.placeholder},model:{value:e.formData[t.prop],callback:function(a){e.$set(e.formData,t.prop,a)},expression:"formData[item.prop]"}},e._l(t.options,function(e){return a("bk-option",{key:e.id,attrs:{id:e.id,name:e.name}})}),1):a("bk-input",{directives:[{name:"test",rawName:"v-test",value:"tempInput",expression:"'tempInput'"}],attrs:{"test-key":t.prop,clearable:t.clearable,placeholder:t.placeholder},model:{value:e.formData[t.prop],callback:function(a){e.$set(e.formData,t.prop,a)},expression:"formData[item.prop]"}})],1)]})],2)],1)};var b=[];var w={props:{},data:function e(){var t={required:true,message:window.i18n.t("必填项"),trigger:"blur"};return{formData:{bk_biz_id:this.$store.state.bizId,template_name:"",file_name:"",abs_path:"",owner:"",group:"",filemode:"0775",line_separator:"LF"},formItems:[{label:this.$t("模板名称"),required:true,prop:"template_name",clearable:true,placeholder:this.$t("模板唯一标识")},{label:this.$t("文件名称"),required:true,prop:"file_name",clearable:true,placeholder:this.$t("模板渲染生成的文件名称")},{label:this.$t("文件所处路径"),required:true,prop:"abs_path",clearable:true,placeholder:this.$t("文件分发到服务器的路径")},{label:this.$t("文件拥有者"),required:true,prop:"owner",clearable:true,placeholder:this.$t("拥有者名称，操作系统必须存在此用户")},{label:this.$t("文件用户组"),required:true,prop:"group",clearable:true,placeholder:this.$t("用户组名称，操作系统必须存在此用户组")},{label:this.$t("文件权限"),required:true,prop:"filemode",clearable:true,placeholder:this.$t("文件的权限设置，如0775")},{label:this.$t("输出格式"),required:true,prop:"line_separator",clearable:true,placeholder:this.$t("请选择文件输出格式"),type:"select",options:[{id:"CRLF",name:"CRLF - Windows（\\r\\n）"},{id:"LF",name:"LF - Unix and macOS（\\n）"}]}],rules:{template_name:[t],file_name:[t],abs_path:[t,{validator:function e(t){return t.match(/^\/|^[a-zA-Z]:[\\]/)},message:this.$t("路径格式非法，请检查绝对路径格式是否正确"),trigger:"blur"}],owner:[t,{validator:function e(t){return t.match(/^[a-zA-Z][a-zA-Z0-9]*$/)},message:this.$t("请输入英文字母或数字，且必须以英文字母开头"),trigger:"blur"}],group:[t,{validator:function e(t){return t.match(/^[a-zA-Z][a-zA-Z0-9]*$/)},message:this.$t("请输入英文字母或数字，且必须以英文字母开头"),trigger:"blur"}],filemode:[t,{validator:function e(t){return t.match(/^[0-7]{4}$/)},message:this.$t("文件权限设置提示"),trigger:"blur"}],line_separator:[t]}}},methods:{}};var k=w;var $=a(760);var C=a(10);var x=Object(C["a"])(k,_,b,false,null,"367ede2d",null);var T=x.exports;var S=a(644);var y=a(544);var L={components:{BasicInfo:T,ProcessSelect:S["a"]},mixins:[y["a"]],props:{showCreate:{type:Boolean,default:false}},data:function e(){return{dialogHeight:618,isFirstStep:true,createLoading:false,newTemplate:{},bindLoading:false}},methods:{handleValueChange:function e(t){this.$emit("update:showCreate",t);if(!t){this.isFirstStep=true;this.createLoading=false;this.newTemplate={};this.bindLoading=false}},handleCreate:function e(){var t=this;return m()(s.a.mark(function e(){var a;return s.a.wrap(function e(r){while(1){switch(r.prev=r.next){case 0:r.prev=0;r.next=3;return t.$refs.basicInfo.$refs.form.validate();case 3:t.createLoading=true;r.next=6;return t.$store.dispatch("configTemplate/ajaxCreateConfigTemplate",{data:t.$refs.basicInfo.formData});case 6:a=r.sent;a.data.config_template_id+="";t.newTemplate=a.data;t.isFirstStep=false;t.messageSuccess("配置文件模板，新建成功。");r.next=16;break;case 13:r.prev=13;r.t0=r["catch"](0);console.warn(r.t0);case 16:r.prev=16;t.createLoading=false;return r.finish(16);case 19:case"end":return r.stop()}}},e,null,[[0,13,16,19]])}))()},handleCancel:function e(){this.$emit("update:showCreate",false)},handleBind:function e(){var t=this;return m()(s.a.mark(function e(){var a,r,n,i,o;return s.a.wrap(function e(s){while(1){switch(s.prev=s.next){case 0:s.prev=0;t.bindLoading=true;a=t.$refs.processSelect,r=a.templateProcess,n=a.instanceProcess;if(!(!r.length&&!n.length)){s.next=6;break}t.handleSkip();return s.abrupt("return");case 6:i=[];r.forEach(function(e){i.push({process_object_type:"TEMPLATE",process_object_id:e.id})});n.forEach(function(e){i.push({process_object_type:"INSTANCE",process_object_id:e.property.bk_process_id})});o=Number(t.newTemplate.config_template_id);s.next=12;return t.$store.dispatch("configTemplate/ajaxBindTemplateToProcess",{templateId:o,data:{process_object_list:i}});case 12:t.messageSuccess(t.$t("关联成功"));t.$emit("created",t.newTemplate.config_template_id);s.next=19;break;case 16:s.prev=16;s.t0=s["catch"](0);console.warn(s.t0);case 19:s.prev=19;t.bindLoading=false;return s.finish(19);case 22:case"end":return s.stop()}}},e,null,[[0,16,19,22]])}))()},handleSkip:function e(){var t=this;this.$bkInfo({title:this.$t("请确认是否跳过关联进程"),subTitle:this.$t("该配置文件尚未关联进程"),confirmFn:function e(){return t.$emit("created",t.newTemplate.config_template_id)}})}}};var N=L;var P=Object(C["a"])(N,h,g,false,null,null,null);var F=P.exports;var I=a(646);var D=a(19);function j(e,t){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter(function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable})),a.push.apply(a,r)}return a}function O(e){for(var t=1;t<arguments.length;t++){var a=null!=arguments[t]?arguments[t]:{};t%2?j(Object(a),!0).forEach(function(t){v()(e,t,a[t])}):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):j(Object(a)).forEach(function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(a,t))})}return e}var z={name:"TemplateList",components:{CreateTemplateDialog:F,BindProcessDialog:I["a"]},data:function e(){return{commonFilterMethod:D["c"],formatDate:D["e"],searchWord:"",ordering:"",searchedWord:"",templateLoading:true,templateList:[],updatePersonFilters:[],templateItem:{},pagination:{current:1,count:0,limit:50},showCreate:false,showBindProcess:false}},computed:O({},Object(f["d"])(["authMap"])),created:function e(){this.getTemplateList()},mounted:function e(){var t=this.$route.query.fromPreManage;if(t){this.showCreate=true}},methods:{getTemplateList:function e(){var t=this;return m()(s.a.mark(function e(){var a,r;return s.a.wrap(function e(n){while(1){switch(n.prev=n.next){case 0:n.prev=0;t.templateLoading=true;n.next=4;return t.$store.dispatch("configTemplate/ajaxGetConfigTemplateList",{search:t.searchWord,ordering:t.ordering,page:t.pagination.current,pagesize:t.pagination.limit});case 4:a=n.sent;r=new Set;a.data.list.forEach(function(e){e.config_template_id+="";r.add(e.updated_by);p()(e,e.permission||{})});t.updatePersonFilters=l()(r).map(function(e){return{text:e,value:e}});t.templateList=a.data.list;t.pagination.count=a.data.count;t.searchedWord=t.searchWord;n.next=20;break;case 13:n.prev=13;n.t0=n["catch"](0);t.templateList.splice(0);t.updatePersonFilters.splice(0);t.pagination.current=1;t.pagination.count=0;console.warn(n.t0);case 20:n.prev=20;t.templateLoading=false;return n.finish(20);case 23:case"end":return n.stop()}}},e,null,[[0,13,20,23]])}))()},handleSearch:function e(){if(this.searchWord!==this.searchedWord){this.pagination.current=1;this.getTemplateList()}},handleSortChange:function e(t){var a=t.prop,r=t.order;if(r==="ascending"){this.ordering=a}else if(r==="descending"){this.ordering="-".concat(a)}else{this.ordering=""}this.getTemplateList()},handlePageChange:function e(t){this.pagination.current=t;this.getTemplateList()},handlePageLimitChange:function e(t){this.pagination.current=1;this.pagination.limit=t;this.getTemplateList()},operateVersionList:function e(t){this.$emit("selectConfig",t);this.$store.commit("routeConfigTemplateVersionList",{templateId:t.config_template_id})},operateDistribute:function e(t){this.$emit("selectConfig",t);this.$store.commit("routeConfigTemplateDistribute",{templateId:t.config_template_id})},operateGenerate:function e(t){this.$emit("selectConfig",t);this.$store.commit("routeConfigTemplateGenerate",{templateId:t.config_template_id})},operatePreview:function e(t){this.$emit("selectConfig",t);this.$store.commit("routeConfigTemplateVersionDetail",{templateId:t.config_template_id,versionId:0,isPreview:true})},operateBind:function e(t){this.templateItem=t;this.showBindProcess=true},operateDelete:function e(t){var a=this;this.$bkInfo({title:"".concat(this.$t("确认要删除"),"【").concat(t.template_name,"】").concat(this.$t("？")),width:540,confirmLoading:true,confirmFn:function(){var e=m()(s.a.mark(function e(){return s.a.wrap(function e(r){while(1){switch(r.prev=r.next){case 0:r.prev=0;r.next=3;return a.$store.dispatch("configTemplate/ajaxDeleteConfigTemplate",{templateId:t.config_template_id});case 3:a.messageSuccess(a.$t("删除成功"));a.getTemplateList();return r.abrupt("return",true);case 8:r.prev=8;r.t0=r["catch"](0);console.warn(r.t0);return r.abrupt("return",false);case 12:case"end":return r.stop()}}},e,null,[[0,8]])}));function r(){return e.apply(this,arguments)}return r}()})},handleCreated:function e(t){this.$emit("selectConfig",t)}}};var E=z;var A=a(763);var B=Object(C["a"])(E,r,n,false,null,"d8797614",null);var q=t["default"]=B.exports},541:function(e,t,a){},545:function(e,t,a){},760:function(e,t,a){"use strict";var r=a(541);var n=a.n(r);var i=n.a},763:function(e,t,a){"use strict";var r=a(545);var n=a.n(r);var i=n.a}}]);