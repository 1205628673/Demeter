<template>
  <div id="app">
    <HelloWorld msg="Welcome to Your Vue.js App"/>
    <SimpleTable />
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
import SimpleTable from './components/SimpleTable.vue'

export default {
  name: 'App',
  components: {
    HelloWorld,
    SimpleTable
  }
}
</script>

<style>

</style>
