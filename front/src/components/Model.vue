<template>
    <div class='container'>
        <el-table
            :data='tableData'
            style="width: 100%;"
            :cell-style="rowStyle">
            <el-table-column
                prop='id'
                label='ID'
                header-align='center'
                width='120px'>
            </el-table-column>
            <el-table-column
                prop='time'
                label='建模时间'
                header-align='center'
                width='120px'>
            </el-table-column>
            <el-table-column
                prop='regressor'
                label='模型回归器类型'
                header-align='center'
                width='120px'>
            </el-table-column>
            <el-table-column
                prop='fid'
                label='文件ID'
                header-align='center'>
            </el-table-column>
            <el-table-column
                prop='state'
                label='状态'
                header-align='center'>
            </el-table-column>
            <el-table-column
                label='操作'
                header-align='center'
                width='400px'>
                <template slot-scope='scope'>
                    <div class='option' v-if='scope.row.id'>
                        <el-button type='success' @click='iter(scope.row)'>收敛过程</el-button>
                        <el-button type='primary' @click='chooseFileList(scope.row)'>回归预测</el-button>
                        <el-button type='danger' @click='deleteCustomizeModel(scope.row)'>删除模型</el-button>
                    </div>
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
            :visible='iterDialogVisible'
            @close="closeDialog('iter')"
            width='70%'>
            <div class='draw-panel'>   
                <div id='iterationLine' ref="iterationLine" style='height:500px;'/>
            </div> 
        </el-dialog>
        <el-dialog
            :visible='predictDialogVisible'
            @close="closeDialog('predict')"
            width='70%'>
            <div class='draw-panel'>
                <div class='box-flex'> 
                    <div class='evaluation'>
                        <p>R2={{this.r2}}</p>
                        <p>RMSE={{this.rmse}}</p>
                        <p>MAPE={{this.mape}}</p>
                        <p>RPD={{this.rpd}}</p>
                    </div>
                    <div id='resultLine' ref="resultLine" style='height:500px;'/>
                    <div id='resultPoint' ref="resultPoint" style='height:500px;'/>
                </div>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="closeDialog('predict')">确 定</el-button>
            </span>
        </el-dialog>
        <el-dialog
            :visible='fileDialogVisible'
            @close="closeDialog('file')"
            width='70%'
            v-loading="predictResultLoading">
            <div class='draw-panel'>
                <div class='box-flex'> 
                    <div class='file-list'>
                        <el-table
                            :data="fileData"
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
                                    <el-button type="danger" @click='toPredict(scope.row)'>预测分析</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
            </div>
        </el-dialog>
    </div>
</template>
<script>
    import {get,deleted} from '../request/http'

    export default {
        data() {
            return {
                page:0,     // 自定义模型列表的页数
                pageSize:0,     
                total:0,
                filePage:0,     // 可用于预测的文件列表的页数
                filePageSize:0,
                fileTotal:0,
                r2:0.0,     //预测数据的r2
                rmse:0.0,   //预测数据的均方根误差
                mape:0.0,
                rpd:0.0,
                iterDialogVisible:false,    //控制收敛过程模态框的boolean值
                predictDialogVisible:false,     //控制自定义模型预测模态框
                fileDialogVisible:false,        //控制用于预测的文件模态框
                selectedModelId:-1,     //表示要进行预测的自定义模型
                tableData:[],       //所有自定义模型的数据
                fileData:[],        //所有被用于预测的文件数据
                predictResultLoading:true,     //用于控制加载预测数据时候的转圈 
                bestFitnessValues:[],       //被选中模型的收敛过程中的最佳适应度曲线数据
                meanFitnessValues:[]        //被选中模型的收敛过程中的平均适应度曲线数据
            }
        },
        methods:{
            chooseFileList(e) {
                var modelId = e.id
                this.selectedModelId = modelId
                this.fileDialogVisible = true
            },
            deleteCustomizeModel(e) {
                var modelId = e.id
                deleted('/api/delete/model',{'mid':modelId}).then(res => {
                    if(res.code == 200) {
                        this.$message({
                            type:'success',
                            message:res.message
                        })
                    }
                    else{
                        this.$message.error(res.message)
                    }
                })
            },
            findAllFile(page) {
                get('/api/findall',{'page':page}).then(res => {
                    if(res.code == 200) {
                        var fileMappers = res.data
                        this.filePage = res.page
                        this.fileTotal = res.total
                        this.filePageSize = res.pageSize
                        for(var i =0; i < fileMappers.length;i++) {
                            var row = {filename:fileMappers[i].filename, id:fileMappers[i].id}
                            this.fileData.push(row)
                        }
                    }
                    else {
                        this.$message.error(res.message)
                    }
                })
            },
            findModel(page) {
                get('/api/trainjob',{'page':page}).then(res => {
                    if(res.code == 200) {
                        var model_list = res.data
                        for(var i = 0; i < model_list.length; i++) {
                            let model = model_list[i]
                            let id = model.id
                            let fid = model.fid
                            let regressor = model.regressor
                            let time = model.time
                            let state = ''
                            let bestFitnessValues = []
                            let meanFitnessValues = []
                            if(!model.path) {
                                state = '正在训练中'
                            }
                            else{
                                state = '已完成'
                                bestFitnessValues = model.best_fitness_values
                                meanFitnessValues = model.mean_fitness_values
                            }
                            let rowData = {
                                id : id,
                                fid : fid,
                                regressor : regressor,
                                time : time,
                                state : state,
                                bestFitnessValues : bestFitnessValues,
                                meanFitnessValues : meanFitnessValues
                            }
                            this.tableData.push(rowData)
                            this.page = res.page
                            this.total = res.total
                            this.pageSize = res.pageSize
                        }
                    }
                    else {
                        this.$message.error(res.message)
                    }
                })
            },
            iter(e) {
                this.iterDialogVisible = true
                var regressor = e.regressor
                console.info(e.meanFitnessValues)
                setTimeout(()=>{
                    let myLineChart = this.$echarts.init(this.$refs.iterationLine)
                    let round = []
                    for(var i =0;i<e.bestFitnessValues.length;i++) {
                        round.push(i)
                    }
                    myLineChart.setOption({
                        title: { text: regressor+'收敛过程'},
                        tooltip: {},
                        legend: {
                            data: ['Best fitness value', 'mean fitness value']
                        },
                        xAxis: {
                            data : round,
                            name: 'iteration round'
                        },
                        yAxis: {
                            type: 'value',
                            name: 'fitness value'
                        },
                        series: [
                            {
                                name: 'Best fitness value',
                                type: 'line',
                                data: e.bestFitnessValues
                            },
                            {
                                name: 'mean fitness value',
                                type: 'line',
                                data: e.meanFitnessValues
                            }
                        ]
                    })
                    this.iterDialogVisible = true
                },1)
            },
            toPredict(e) {
                this.fileDialogVisible = false
                this.predictDialogVisible = true
                var fileId  = e.id
                var modelId = this.selectedModelId
                get('/api/customize/predict',{'mid':modelId, 'fid':fileId}).then(res => {
                    if(res.code == 200) {
                        this.predictResultLoading = false   //关掉数据加载时的遮罩
                        let data = res.data
                        this.preds = data.preds
                        this.labels = data.labels
                        this.level = data.level
                        this.rmse = data.rmse
                        this.mape = data.mape
                        this.rpd = data.rpd
                        this.r2 = data.r2
                        this.predictResultLoading = false
                        var number = []
                        for(let i = 0;i < this.preds;i++) {
                            number.push(i)
                        }
                        var pointArr = new Array(this.preds.length)
                        for(let j =0;j < pointArr.length;j++) {
                            pointArr[j] = new Array(2)
                        }
                        for(let i = 0;i<this.preds.length;i++) {
                            pointArr[i] = [this.labels[i], this.preds[i]]
                        }
                        let myPointChart = this.$echarts.init(document.getElementById('resultPoint'))
                        myPointChart.setOption({
                            xAxis: {name: 'observe value'},
                            yAxis: {name: 'predict value'},
                            series: [{
                                symbolSize: 10,
                                data: pointArr,
                                type: 'scatter'
                            }]
                        })
                        let myLineChart = this.$echarts.init(document.getElementById('resultLine'))
                        // 绘制图表
                        myLineChart.setOption({
                            title: { text: '回归结果'},
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
                    }
                    else {
                        this.$message.error(res.message)
                    }
                })
            },
            changePage(page) {
                this.findModel(page)
            },
            guide(e) {
                console.info(e)
            },
            rowStyle() {
                return 'text-align:center'
            },
            closeDialog(dialogName) {
                if(dialogName == 'iter') {
                    this.iterDialogVisible = false
                }
                else if(dialogName == 'predict') {
                    this.predictDialogVisible = false
                    this.predictResultLoading = true //打开加载遮罩，再加载预测数据的时候页面转圈
                }
                else if(dialogName == 'file') {
                    this.fileDialogVisible = false
                }
            }
        },
        mounted() {
            this.findModel(1)
            this.findAllFile(1)
        }
    }
</script>
<style>
.pagediv{
    display:flex;
    justify-content:center;
    margin:20px;
}
.option{
    display:flex;
    justify-content:center;
}
</style>