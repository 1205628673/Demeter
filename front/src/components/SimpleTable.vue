<template>
    <div class='container'>
    <el-table
    :data="tableData"
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
    </el-table>
    <el-dialog
        :visible.sync="dialogVisible"
        @close="closeDialog"
        width="60%">
        <div id='myLine' style='height:500px;'/>
        <div id='myPoint' style='height:500px;'/>
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
                mase : 0,
                rmse : 0,
                level : 0
            };
        },
        methods:{
            rowStyle() {
                return "text-align:center"
            },
            closeDialog() {
                this.dialogVisible = false
                this.preds = []
                this.labels = []
                this.mase = 0
                this.rmse = 0
                this.level = 0
                
            },
            guide(e, regressor) {
                var id = e.id
                this.dialogVisible = true
                get('/api/guide',{'fid':id,'regressor':regressor}).then(res => {
                    let data = res.data
                    this.preds = data.preds
                    this.labels = data.labels
                    this.mase = data.mase
                    this.rmse = data.rmse
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
                        pointArr[i] = [this.preds[i], this.labels[i]]
                    }
                    let myPointChart = this.$echarts.init(document.getElementById('myPoint'))
                    myPointChart.setOption({
                        xAxis: {name: 'predict value'},
                        yAxis: {name: 'observe value'},
                        series: [{
                            symbolSize: 10,
                            data: pointArr,
                            type: 'scatter'
                        }]
                    })
                    let myLineChart = this.$echarts.init(document.getElementById('myLine'))
                    // 绘制图表
                    myLineChart.setOption({
                        title: { text: 'rmse '+this.rmse+'\nmase '+this.mase +'\n'},
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
            get('/api/findall').then(res => {
                if(res.code == 200) {
                    var fileMappers = res.data
                    for(var i =0; i < fileMappers.length;i++) {
                        var d = {filename:fileMappers[i].path, id:fileMappers[i].id}
                        this.tableData.push(d)
                    }
                } else{
                    this.$message.error(res.message);
                }
            })
        }
    }
</script>