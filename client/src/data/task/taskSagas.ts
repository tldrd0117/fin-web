import { all, takeEvery } from '@redux-saga/core/effects'
import { runEmitSaga } from '../socket/socketSagas' 
import { fetchTaskState } from './taskSlice'
import { fetchTaskSchedule, addTaskSchedule, removeTaskSchedule } from './taskScheduleSlice'


export function* watchFetchTaskState(){
    yield takeEvery(fetchTaskState, runEmitSaga)
}

export function* watchTaskSchedule(){
    yield all([
        takeEvery(fetchTaskSchedule, runEmitSaga),
        takeEvery(addTaskSchedule, runEmitSaga),
        takeEvery(removeTaskSchedule, runEmitSaga)
    ]);
}