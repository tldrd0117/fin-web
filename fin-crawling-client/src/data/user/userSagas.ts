import { call, put, select, takeEvery } from '@redux-saga/core/effects'
import { push } from 'connected-react-router'
import { getToken, getMe } from './userApi'
import { fetchTokenSuccess, fetchTokenFail, fetchToken } from './userSlice'

export function* watchOnFetchToken(action){
    const {username, password} = action.payload
    const {response, error} = yield call(getToken, username, password)
    console.log(response, error)
    if(response && response.access_token){
        yield put(fetchTokenSuccess({
            token: response.access_token
        }))
        yield put(push("/"))
    } else {
        yield put(fetchTokenFail({response, error}))
    }
}

export function* watchOnToken(){
    yield takeEvery(fetchToken, watchOnFetchToken)
}