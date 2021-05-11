<template>
    <div class='contrainer'>
        <el-table
        :data="tableData.filter(data => !data.filename || data.filename.toLowerCase().includes(search.toLowerCase()))"
        style="width:100%;"
        :cell-style="rowStyle">
        <el-table-column
            prop="filename"
            label="文件名"
            header-align="center">
        </el-table-column>
        <el-table-column
            prop="id"
            label="ID"
            header-align="center">
        </el-table-column>
        <el-table-column
            label="操作"
            header-align="center">
            <template slot-scope='scope'>
                <el-button type='success' @click="train(scope.row, 'svr')">SVR模型训练</el-button>
                <el-button type='success' @click="train(scope.row, 'plsr')">PLSR模型训练</el-button>
                <el-button type='success' @click="train(scope.row, 'bpnn')">BPNN模型训练</el-button>
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
            width="70%">
            <div class="wait-box">
                <div class="wait-text">
                    <p>开始训练模型....</p>
                    <p>这将花费一些时间</p>
                </div>
                <span slot="footer" class="dialog-footer">
                    <el-button type="primary" @click="closeDialog">确 定</el-button>
                </span>
            </div>
        </el-dialog>
    </div>
</template>
<script>
    import {get} from '../request/http'
    export default{
        data(){
            return {
                tableData : [],
                search : '',
                dialogVisible : false,
                meanFitnesses : 0.0,
                bestFitnesses : 0.0,
                page : 1,
                total : 0,
                pageSize : 0
            }
        },
        methods:{
            train(e, regressor) {
                this.dialogVisible = true
                var id = e.id //获得文件id
                get('/api/train', {'fid' : id, 'regressor' : regressor}).then(res => {
                    if(res.code == 200) {
                        this.$message({
                            type:'success',
                            message:res.message
                        })
                    } else{
                        this.$message.error(res.message);
                    }
                })
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
                    } else {
                        this.$message.error(res.message);
                    }
                })
            },
            changePage(page) {
                this.findall(page)
            },
            closeDialog() {
                this.dialogVisible = false
            },
            rowStyle() {
                return "text-align:center"
            }
        },
        mounted(){
            this.findall(1)
        }
    }
</script>
<style>
    .wait-box{
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
    }
</style>