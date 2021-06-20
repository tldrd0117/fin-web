import { take, put, call, apply, delay, takeEvery, all, select, fork, race } from 'redux-saga/effects'
import { EventChannel, eventChannel } from 'redux-saga'
// import { io, Socket } from 'socket.io-client'
import { runCrawling, fetchTasks, reset } from '../crawling/crawlingSlice'
import { connect, disconnect, endConnection, startConnection, destory, create } from '../socket/socketSlice'
import { RootState } from '../root/rootReducer'
import { data } from 'autoprefixer'
import { fetchCompletedTask } from '../crawling/crawlingHistorySlice'
import { push } from 'connected-react-router'

// const socket = io("ws://localhost:8000/ws/"+Date.now(),{
//     transports: ["websocket"]
// })

const socketUrl = process.env.NODE_ENV=="production"?"ws://"+location.host+"/ws/":"ws://localhost:8083/ws/"

function createSocketConnection(token) {
    return eventChannel(emit => {
        let isOpen = false
        let isDisabled = false
        let socket = null
        function createWs(){
            socket = new WebSocket(socketUrl+Date.now()+"?token="+token)
            socket.onopen = function(){
                console.log("socket open")
                isOpen = true
                emit({eventType: "onopen" , data: socket})
            }
            socket.onclose = () => {
                console.log("socket close")
                isOpen = false
                emit({eventType: "onclose" })
                if(!isDisabled){
                    reconnect()
                }
            }
            socket.onerror = function(ev){
                console.log("socket error", ev)
                emit({eventType: "onerror", data: ev})
            }
            socket.onmessage = (ev:MessageEvent<any>) : any => {
                emit({eventType: "onmessage", data: JSON.parse(ev.data)})
            }
        }

        let id = null
        const reconnect = () => {
            clearInterval(id)
            id = setInterval(()=>{
                if(isOpen || isDisabled){
                    clearInterval(id)
                } else {
                    createWs()
                }
            },3000)
        }
        
        // socket.onAny(anyHandler)
        const unsubscribe = () => {
            isDisabled = true;
            console.log("unsubscribe")
            socket.close()
            // socket.offAny(anyHandler)
        }

        createWs()

        return unsubscribe
    })
}

export function* watchOnConnect() {
    let isDoing = true;
    while(isDoing){
        yield race({
            connect: take(connect), 
            disconnect: take(disconnect),
            destory: take(destory)
        })
        const socket = yield select(state => state.socket)
        if(socket.isDestoried){
            isDoing = false;
        }
        console.log("watchOnConnect", socket)
        if(socket.isConnected){
            yield put(fetchTasks({}))
        } else {

        }
    }
}

export function* watchOnSocketConnect(socketConnection) {
    let isDoing = true;
    while(isDoing){
        const channel = yield take(socketConnection)
        if(channel.eventType == "onopen"){
            yield put(connect({ socket: channel.data, socketConnection }))
        } 
        else if(channel.eventType == "onclose"){
            console.log("onclose")
            yield put(disconnect({}))
            yield put(reset({}))
            const {isDestoried} = yield select(state => state.socket)
            if(isDestoried){
                isDoing = false;
            }
        }
        else if(channel.eventType == "onerror"){
            const {isConnected} = yield select(state => state.socket)
            if(!isConnected){
                yield put(connect({ socket: undefined, socketConnection }))
            }
            yield put(push("/login"))
        }
        else if(channel.eventType == "onmessage"){
            const {event, payload} = channel.data
            console.log("event:", event, "payload:", payload)
            yield put({ type: event, payload })
        }
        
    }
}

export function* watchOnStartConnection() {
    while(true){
        yield take(startConnection)
        console.log("startConnection")
        const {isConnected, socketConnection, isDisabled} = yield select(state => state.socket)
        console.log(isConnected)
        if(!isConnected){
            yield put(create({}))
            yield fork(watchOnMessage)
        } else {
            yield put(disconnect({}))
            yield put(reset({}))
            yield put(destory({}))
            socketConnection.close()
        }
    }
}

export function* watchOnEndConnection() {
    while(true){
        yield take(endConnection)
        console.log("endConnection")
        const {isConnected, socketConnection, isDisabled} = yield select(state => state.socket)
        console.log(isConnected, socketConnection)
        yield put(disconnect({}))
        yield put(reset({}))
        yield put(destory({}))
        if(socketConnection)
            socketConnection.close()
    }
}

export function* watchOnSocket() {
    yield fork(watchOnStartConnection)
    yield fork(watchOnEndConnection)
}

export function* watchOnMessage() {
    const {token} = yield select(state => state.user)
    const socketConnection = yield call(createSocketConnection, token)
    yield fork(watchOnConnect)
    yield fork(watchOnSocketConnect, socketConnection)
}

export function* runEmitSaga(action){
    console.log(action)
    const {isConnected, socket} = yield select(state => state.socket)
    if(isConnected && socket){
        yield apply(socket, socket.send, [JSON.stringify({event: action.type, payload: action.payload})])
    }
}

export function* watchEmitData() {
    yield all([
        takeEvery(runCrawling, runEmitSaga),
        takeEvery(fetchTasks, runEmitSaga),
        takeEvery(fetchCompletedTask, runEmitSaga)
    ])
    // yield takeEvery(getTaskHistory, runEmitSaga)
}

