import { all, takeEvery } from "redux-saga/effects";
import { runEmitSaga } from "../socket/socketSagas";
import { fetchCompletedTask  } from "./crawlingHistorySlice";
import { fetchTasks, runCrawling, cancelCrawling, } from "./crawlingSlice";


export function* watchCrawlingReq() {
    yield all([
        takeEvery(runCrawling, runEmitSaga),
        takeEvery(fetchTasks, runEmitSaga),
        takeEvery(fetchCompletedTask, runEmitSaga),
        takeEvery(cancelCrawling, runEmitSaga),
    ])
    // yield takeEvery(getTaskHistory, runEmitSaga)
}
