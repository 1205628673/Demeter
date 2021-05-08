<template>
    <div class='main'>
        <div class='inner'>
        <h1 class='title-word'>DEMETER</h1>
        <el-upload
            class="upload-box"
            drag
            action="/api/upload"
            multiple
            :on-success='uploadSuccess'
            :on-error='uploadError'>
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <div class="el-upload__tip" slot="tip" style='color:white;font-weight:bold;'>只能上传xls/xlsx文件，且不超过500kb，并且按照要求的样本格式上传</div>
        </el-upload>
        </div>
    </div>
</template>
<script>
    export default{
        data(){
            return {

            }
        },
        methods:{
            uploadSuccess(){
                this.$message({
                    message: '上传成功',
                    type:'success'
                })
            },
            uploadError(){
                this.$message.error('上传失败')
            }
        }
    }
</script>
<style>
    .main{
        height:100%;
        width:100%;
        margin:0px;
        padding:0px;
        position:absolute;
        background-image:url('../assets/demeterg2.jpeg');
        background-size:cover;
        display:flex;
        align-items:center;
        justify-content:center;
        text-align:center;
    }
    .upload-box{
        opacity:0.5;
    }
    .title-word{
        font-family:Slab;
        font-style:oblique;
        color:white;
        font-size:100px;
    }
</style>