import { take, put, call, apply, delay, takeEvery } from 'redux-saga/effects'
import { eventChannel } from 'redux-saga'
// import { io, Socket } from 'socket.io-client'
import { runCrawling, getTaskHistory } from '../crawling/crawlingSlice'
import { connect, disconnect } from '../socket/socketSlice'

// const socket = io("ws://localhost:8000/ws/"+Date.now(),{
//     transports: ["websocket"]
// })

let socket = null

function createSocketConnection() {
    return new Promise(function(resolve, reject){
        socket = new WebSocket("ws://localhost:8000/ws/"+Date.now())
        socket.onopen = function(){
            console.log("socket open")
            resolve(socket)
            // ev.data
        }
        socket.onerror = function(ev){
            console.log("socket close")
            reject("close")
        }

        // socket.on("connect",() => {
        //     console.log("socket connect")
        //     socket.emit("crawling/checkDoingCrawling")
        //     resolve(socket)
        // })
        // socket.on("disconnect", (reason) => {
        //     console.log("socket disconnect")
        //     reject(reason)  
        // })
    })
}

function createSocketChannel() {
    return eventChannel(emit => {
        let isOpen = false
        function createWs(){
            socket = new WebSocket("ws://localhost:8000/ws/"+Date.now())
            socket.onopen = function(){
                console.log("socket open")
                isOpen = true
                // ev.data
            }
            socket.onerror = function(ev){
                console.log("socket error")
            }
            socket.onmessage = (ev:MessageEvent<any>) : any => {
                emit(JSON.parse(ev.data))
            }
            socket.onclose = () => {
                console.log("socket close")
                isOpen = false
                reconnect()
            }
        }

        let id = null
        const reconnect = () => {
            clearInterval(id)
            id = setInterval(()=>{
                if(isOpen){
                    clearInterval(id)
                } else {
                    createWs()
                }
            },3000)
        }
        
        // socket.onAny(anyHandler)
        const unsubscribe = () => {
            console.log("unsubscribe")
            socket.close()
            // socket.offAny(anyHandler)
        }

        createWs()

        return unsubscribe
    })
}

export function* watchOnMessage() {
    try{
        // const socket: WebSocket = yield call(createSocketConnection)
        const socketChannel = yield call(createSocketChannel)
        yield put(connect({}))
        while(true){
            try{
                const {event, payload} = yield take(socketChannel)
                console.log("payload:",payload)
                yield put({ type: event, payload})
            } catch(e) {
                console.error('socket error:', e)
                yield put(disconnect({}))
                socketChannel.close()
                socket.close()
            }
        }
    } catch(e){
        yield put(disconnect({}))
        if(e=="close"){
            console.log("cloooo")
        }
        
    }
    
}

export function* runEmitSaga(action){
    console.log(action)
    yield apply(socket, socket.send, [JSON.stringify({event: action.type, payload: action.payload})])
}

export function* watchRunCrawling() {
    yield takeEvery(runCrawling, runEmitSaga)
    // yield takeEvery(getTaskHistory, runEmitSaga)
}

