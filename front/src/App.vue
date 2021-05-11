<template>
  <div id="app">
    <el-header>
    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect" router>
      <el-menu-item index='/upload'>Demeter</el-menu-item>
      <el-menu-item index="/index">处理中心</el-menu-item>
      <el-menu-item index="/train">训练中心</el-menu-item>
      <el-menu-item index='/model'>模型中心</el-menu-item>
    </el-menu>
  </el-header>
  <router-view />
  </div>
</template>

<script>

export default {
  name: 'App',
  data() {
    return {
      activeIndex : '1'
    };
  },
  methods:{
    handleSelect(key, path) {
      console.log(key,path)
      this.activeIndex = key
    }
  }
}
</script>

<style>
*{
  margin:0;
  padding:0;
  border:0;
}
</style>
