<template>
    <div class='detail'>
    <el-table
        :data="sampleData.filter(data => !data.somValue || (data.somValue < high && data.somValue > lower))"
        style="width: 100%"
        :cell-style="rowStyle">
        <el-table-column
            prop='id'
            label='ID'
            header-align='center'>
        </el-table-column>
        <el-table-column
            prop='fid'
            label='File ID'
            header-align='center'>
        </el-table-column>
        <el-table-column
            prop='sid'
            label='Sample ID'
            header-align='center'>
        </el-table-column>
        <el-table-column
            prop='somValue'
            label='有机质含量 g/kg-1'
            header-align='center'>
        </el-table-column>
        <el-table-column
            prop='regressor'
            label='回归模型'
            header-align='center'>
        </el-table-column>
        <el-table-column>
        <!-- eslint-disable -->
            <template slot="header" slot-scope="scope">
                <el-input
                v-model="lower"
                size="mini"
                placeholder="最低" />
            </template>
        </el-table-column>
        <el-table-column>
        <!-- eslint-disable -->
            <template slot="header" slot-scope="scope">
                <el-input 
                v-model='high'
                size='mini'
                placeholder='最高' />
            </template>
        </el-table-column>
    </el-table>
    <div class='pagediv'>
        <el-pagination
            background
            layout='prev, pager, next'
            :total='this.total'
            :current-page='this.page'
            :page-size='this.pageSize'
            @current-change='changePage'>
        </el-pagination>
    </div>
    </div>
</template>
<script>
    import {get} from '../request/http'
    export default {
        data() {
            return {
                sampleData:[],
                page : 1,
                total : 0,
                pageSize : 0,
                fid : 0,
                regressor : '',
                lower : '',
                high : ''
            }
        },
        methods:{
            rowStyle() {
                return "text-align:center"
            },
            findSample(fid, regressor, page){
                get('/api/findsample',{'fid':fid, 'regressor':regressor, 'page':page}).then(res => {
                    var data = res.data
                    this.sampleData = data
                    this.page = res.page
                    this.total = res.total
                    this.pageSize = res.pageSize
                })
            },
            changePage(page){
                this.findSample(this.fid,this.regressor,page)
            },
        },
        mounted() {
            var query = this.$route.query
            for(let key in query) {
                let val = query[key]
                if(key == 'fid') {
                    this.fid = val
                } else if(key == 'regressor') {
                    this.regressor = val
                }
            }
            this.findSample(this.fid, this.regressor, 1)
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