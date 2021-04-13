import axios from 'axios'
import qs from 'qs'

axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8';

//export 将方法暴露出去，让组件引入
export function get(url,params){
    return new Promise((resolve,reject) => {
        axios.get(url,{
            params:params
        }).then(res =>{
            resolve(res.data)
        }).catch(res => {
            reject(res.data)
        })
    })
}
export function deleted (url,params){
    return new Promise((resolve,reject) => {
        axios.delete(url,{
            params:params
        }).then(res =>{
            resolve(res.data)
        }).catch(res => {
            reject(res.data)
        })
    })
}
export function post(url,params){
    return new Promise((resolve,reject) => {
        axios.post(url,qs.stringify(params))
        .then(res => {
            resolve(res.data)
        })
        .catch(res => {
            reject(res.data)
        })
    })
}

export function put(url,params){
    return new Promise((resolve,reject) => {
        axios.put(url,params)
        .then(res => {
            resolve(res.data)
        })
        .catch(res => {
            reject(res.data)
        })
    })
}

