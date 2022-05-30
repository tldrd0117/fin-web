import { call, put, select, takeEvery } from '@redux-saga/core/effects'
import { push } from 'connected-react-router'
import { show } from '../modal/modalSlice'
import { getToken, getMe, join, getPublicKey } from './userApi'
import { fetchTokenSuccess, fetchTokenFail, fetchToken, joinSuccess, joinFail, submitJoin, fetchPublicKeySuccess, fetchPublicKeyFail, fetchPublicKey } from './userSlice'

export function* watchOnFetchToken(action){
    yield put(show({
        modalName: "LoadingModal",
        isShow: true
    }))
    const {username, encPassword} = action.payload
    const {response, error} = yield call(getToken, username, encPassword)
    yield put(show({
        modalName: "LoadingModal",
        isShow: false
    }))
    console.log(response, error)
    if(response && response.accessToken && !response.detail){
        yield put(fetchTokenSuccess({
            token: response.accessToken
        }))
        yield put(push("/"))
    } else {
        yield put(fetchTokenFail({response, error}))
    }
}

export function* watchOnJoin(action){
    const {username, encPassword, email, salt} = action.payload
    const {response, error} = yield call(join, username, encPassword, email, salt)
    console.log(response, error)
    if(response && !response.detail){
        yield put(joinSuccess({
            id: response
        }))
        yield put(push("/login"))
    } else {
        yield put(joinFail({response, error}))
    }
}

export function* watchOnPublicKey(action){
    yield put(show({
        modalName: "LoadingModal",
        isShow: true
    }))
    const {response, error} = yield call(getPublicKey)
    console.log(response, error)
    yield put(show({
        modalName: "LoadingModal",
        isShow: false
    }))
    if(response && !response.detail){
        yield put(fetchPublicKeySuccess(response))
    } else {
        yield put(fetchPublicKeyFail({response, error}))
    }
}


export function* watchOnToken(){
    yield takeEvery(fetchToken, watchOnFetchToken)
    yield takeEvery(submitJoin, watchOnJoin)
    yield takeEvery(fetchPublicKey, watchOnPublicKey)
}