import { all, takeEvery, put} from '@redux-saga/core/effects'
import { runEmitSaga } from '../socket/socketSagas' 
import { fetchTaskSchedule, addTaskSchedule, removeTaskSchedule, fetchTaskScheduleRes } from './taskScheduleSlice'
import { fetchTaskState, fetchTaskStateRes, updateTaskStateRes } from './taskCalendarSlice'
import { addTask, fetchTasks, cancelTask, fetchTasksRes } from './taskProgressSlice'
import { fetchCompletedTask, fetchCompletedTaskRes } from './taskHistorySlice'
import { show } from '../modal/modalSlice'


function* watchRequest(action){
    yield put(show({
        modalName: "LoadingModal",
        isShow: true
    }))
    yield runEmitSaga(action)
}

function* watchResponse(action){
    yield put(show({
        modalName: "LoadingModal",
        isShow: false
    }))
}

export function* watchTasks(){
    yield all([
        takeEvery(addTask, watchRequest),
        takeEvery(fetchTasks, watchRequest),
        takeEvery(fetchCompletedTask, watchRequest),
        takeEvery(cancelTask, watchRequest),
        takeEvery(fetchTaskState, watchRequest),
        takeEvery(fetchTaskSchedule, watchRequest),
        takeEvery(addTaskSchedule, watchRequest),
        takeEvery(removeTaskSchedule, watchRequest),
        
        takeEvery(fetchTaskScheduleRes, watchResponse),
        takeEvery(fetchTaskStateRes, watchResponse),
        takeEvery(updateTaskStateRes, watchResponse),
        takeEvery(fetchTasksRes, watchResponse),
        takeEvery(fetchCompletedTaskRes, watchResponse)
    ]);
}