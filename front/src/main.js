import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import axios from 'axios'
import echarts from 'echarts'
Vue.config.productionTip = false
Vue.use(ElementUI)
Vue.prototype.$echarts = echarts
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
}).$mount('#app')
