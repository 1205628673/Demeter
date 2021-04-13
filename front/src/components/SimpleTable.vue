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
        title="回归图"
        :visible.sync="dialogVisible"
        width="60%">
        <canvas id='myCanvas' style='width:600px;height:400px;maring-top:100px'/>
        <span slot="footer" class="dialog-footer">
            <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
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
            rowStyle(){
                return "text-align:center"
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