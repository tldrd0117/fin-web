import { take, put, call, apply, delay, takeEvery } from 'redux-saga/effects'
import { eventChannel } from 'redux-saga'
import { io, Socket } from 'socket.io-client'
import { runCrawling, getTaskHistory } from '../crawling/crawlingSlice'
import { connect, disconnect } from '../socket/socketSlice'

const socket = io("http://localhost:8083")

function createSocketConnection() {
    return new Promise(function(resolve, reject){
        socket.on("connect",() => {
            console.log("socket connect")
            socket.emit("crawling/checkDoingCrawling")
            resolve(socket)
        })
        socket.on("disconnect", (reason) => {
            console.log("socket disconnect")
            reject(reason)  
        })
    })
}

function createSocketChannel(socket: Socket) {
    return eventChannel(emit => {
        const anyHandler = (event, payload) => {
            console.log(event, payload)
            emit({event, payload})
        }
        socket.onAny(anyHandler)
        const unsubscribe = () => {
            socket.offAny(anyHandler)
        }

        return unsubscribe
    })
}

export function* watchOnMessage() {
    try{
        const socket: Socket = yield call(createSocketConnection)
        yield put(connect({}))
        const socketChannel = yield call(createSocketChannel, socket)
        while(true){
            try{
                const {event, payload} = yield take(socketChannel)
                console.log(payload)
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

    }
    
}

export function* runEmitSaga(action){
    console.log(action)
    yield apply(socket, socket.emit, [action.type, action.payload])
}

export function* watchRunCrawling() {
    yield takeEvery(runCrawling, runEmitSaga)
    yield takeEvery(getTaskHistory, runEmitSaga)
}

