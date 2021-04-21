<template>
    <div class='container'>
    <el-table
    :data="tableData.filter(data => !data.filename || data.filename.toLowerCase().includes(search.toLowerCase()))"
    style="width: 100%;"
    :cell-style="rowStyle">
    <el-table-column
      prop="filename"
      label="文件名"
      width="180"
      header-align="center">
    </el-table-column>
    <el-table-column
      prop="id"
      label="ID"
      width="180"
      header-align="center">
    </el-table-column>
    <el-table-column
        label="操作"
        header-align="center">
        <template slot-scope='scope'>
            <el-button type="primary" @click='guide(scope.row, "svr")'>SVR回归</el-button>
            <el-button type="danger" @click='guide(scope.row, "plsr")'>PLSR回归</el-button>
            <el-button type="warning" @click='guide(scope.row, "bpnn")'>BPNN回归</el-button>
            <el-button type="success" @click='guide(scope.row, "bp")'>BPNN-PLSR回归</el-button>
        </template>
    </el-table-column>
    <el-table-column>
    <!-- eslint-disable -->
        <template slot="header" slot-scope="scope">
            <el-input 
                v-model='search'
                size='mini'
                placeholder='文件名'/>
        </template>
    </el-table-column>
    </el-table>
    <div class='pagediv'>
        <el-pagination
        background
        layout="prev, pager, next"
        :total='this.total'
        :current-page='this.page'
        @current-change='changePage'
        :page-size='this.pageSize'>
        </el-pagination>
    </div>
    <el-dialog
        :visible.sync="dialogVisible"
        @close="closeDialog"
        width="60%">
        <div id='myLine' style='height:500px;'/>
        <div id='myPoint' style='height:500px;'/>
        <el-button type="info" @click="gotoDetail">查看样本</el-button>
        <span slot="footer" class="dialog-footer">
            <el-button type="primary" @click="closeDialog">确 定</el-button>
        </span>
    </el-dialog>
    </div>
</template>
<script>
import {get} from '../request/http'
    export default{
        data() {
            return {
                tableData: [],
                dialogVisible:false,
                preds : [],
                labels : [],
                page : 1,
                total : 0,
                pageSize : 0,
                level : 0,
                dialogFid : 0,
                dialogRegressor : '',
                search:''
            }
        },
        methods:{
            rowStyle() {
                return "text-align:center"
            },
            closeDialog() {
                this.dialogVisible = false
                this.preds = []
                this.labels = []
                this.level = 0  
            },
            gotoDetail() {
                this.$router.push({path:'/sampledetail', query:{fid:this.dialogFid, regressor:this.dialogRegressor}})
            },
            findall(page) {
                get('/api/findall', {'page':page}).then(res => {
                    if(res.code == 200) {
                        var fileMappers = res.data
                        this.page = res.page
                        this.total = res.total
                        this.pageSize = res.pageSize
                        for(var i =0; i < fileMappers.length;i++) {
                            var d = {filename:fileMappers[i].filename, id:fileMappers[i].id}
                            this.tableData.push(d)
                        }
                    } else{
                        this.$message.error(res.message);
                    }
                })
            },
            changePage(page) {
                this.findall(page)
            },
            guide(e, regressor) {
                var id = e.id
                this.dialogVisible = true
                this.dialogFid = e.id
                this.dialogRegressor = regressor
                get('/api/guide',{'fid':id,'regressor':regressor}).then(res => {
                    let data = res.data
                    this.preds = data.preds
                    this.labels = data.labels
                    this.level = data.level
                    var number = []
                    for(let i = 0;i < this.preds;i++) {
                        number.push(i)
                    }
                    var pointArr = new Array(this.preds.length)
                    for(let j =0;j < pointArr.length;j++) {
                        pointArr[j] = new Array(2)
                    }
                    for(let i = 0;i<this.preds.length;i++) {
                        pointArr[i] = [i, this.preds[i]]
                    }
                    let myPointChart = this.$echarts.init(document.getElementById('myPoint'))
                    myPointChart.setOption({
                        xAxis: {name: 'predict value'},
                        yAxis: {name: 'number of sample'},
                        series: [{
                            symbolSize: 10,
                            data: pointArr,
                            type: 'scatter'
                        }]
                    })
                    let myLineChart = this.$echarts.init(document.getElementById('myLine'))
                    // 绘制图表
                    myLineChart.setOption({
                        title: { text:  regressor +'回归'},
                        tooltip: {},
                        legend: {
                            data: ['observe', 'predict']
                        },
                        xAxis: {
                            data: number,
                            name: 'number of sample'
                        },
                        yAxis: {
                            type: 'value',
                            name: 'som value'
                        },
                        series: [
                            {
                                name: 'observe',
                                type: 'line',
                                data: this.labels
                            },
                            {
                                name: 'predict',
                                type: 'line',
                                data: this.preds
                            }
                        ]
                    });
                })
            }
        },
        mounted() {
            this.findall(1)
        }
    }
</script>
<style>
.pagediv{
    display:flex;
    justify-content:center;
    margin:20px;
}
</style>