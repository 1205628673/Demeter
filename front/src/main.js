import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import axios from 'axios'
import VueRouter from 'vue-router'
import echarts from 'echarts'
import simpleTable from './components/SimpleTable.vue'
import upload from './components/Upload.vue'
import sampleDetail from './components/SampleDetail.vue'
import train from './components/Train.vue'
import model from './components/Model.vue'

Vue.config.productionTip = false
Vue.use(ElementUI)
Vue.use(VueRouter)
Vue.prototype.$echarts = echarts
const routes = [
    { path: '/', component : simpleTable},
    { path : '/index', component : simpleTable },
    { path : '/upload', component : upload},
    { path : '/sampledetail', component : sampleDetail},
    { path : '/train', component : train},
    { path : '/model', component : model}
]
const router = new VueRouter({
      routes: routes
})
axios.interceptors.response.use(response => {
  if (response.status == 200) {
    return Promise.resolve(response)
  } else {
    response.data = '服务暂时不可用!';
    return Promise.reject(response)
  }
})
new Vue({
  render: h => h(App),
  router:router
}).$mount('#app')
