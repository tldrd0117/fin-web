import { all, takeEvery } from '@redux-saga/core/effects'
import { runEmitSaga } from '../socket/socketSagas' 
import { fetchTaskSchedule, addTaskSchedule, removeTaskSchedule } from './taskScheduleSlice'
import { fetchTaskState } from './taskCalendarSlice'
import { addTask, fetchTasks, cancelTask } from './taskProgressSlice'
import { fetchCompletedTask } from './taskHistorySlice'


export function* watchTasks(){
    yield all([
        takeEvery(addTask, runEmitSaga),
        takeEvery(fetchTasks, runEmitSaga),
        takeEvery(fetchCompletedTask, runEmitSaga),
        takeEvery(cancelTask, runEmitSaga),
        takeEvery(fetchTaskState, runEmitSaga),
        takeEvery(fetchTaskSchedule, runEmitSaga),
        takeEvery(addTaskSchedule, runEmitSaga),
        takeEvery(removeTaskSchedule, runEmitSaga)
    ]);
}