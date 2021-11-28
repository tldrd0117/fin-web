import { createAction } from '@reduxjs/toolkit'
import { all, put, takeEvery } from 'redux-saga/effects'
import { watchOnSocket } from './socket/socketSagas'
import { addTodo } from './todos/todosSlice'
import { watchOnToken } from './user/userSagas'
import { watchCrawlingReq } from './crawling/crawlingSaga'
import { watchTasks } from './task/taskSagas'
import { watchFactorReq } from './factor/factorSaga'

export const incrementAsync = createAction("INCREMENT_ASYNC")

const delay = (ms) => new Promise(res => setTimeout(res, ms))

export function* incrementAsyncSaga() {
    yield delay(1000)
    yield put(addTodo("saga"))
}

export function* watchIncrementAsync() {
    yield takeEvery(incrementAsync, incrementAsyncSaga)
}

export function* helloSaga(){
    console.log("hello Sagas");
}

export default function* rootSaga(){
    yield all([
        helloSaga,
        watchIncrementAsync(),
        watchOnSocket(),
        watchOnToken(),
        watchCrawlingReq(),
        watchTasks(),
        watchFactorReq()
    ])
}