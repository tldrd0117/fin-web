import { createAction } from '@reduxjs/toolkit'
import { all, put, takeEvery } from 'redux-saga/effects'
import { watchOnMessage, watchRunCrawling } from './socket/socketSagas'
import { addTodo } from './todos/todosSlice'

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
        watchOnMessage(),
        watchRunCrawling()
    ])
}