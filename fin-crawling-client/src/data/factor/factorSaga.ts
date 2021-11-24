import { all, takeEvery } from "redux-saga/effects";
import { runEmitSaga } from "../socket/socketSagas";
import { convertFileToDb, fetchCompletedTask } from "./factorSlice";


export function* watchFactorReq() {
    yield all([
        takeEvery(convertFileToDb, runEmitSaga),
        takeEvery(fetchCompletedTask, runEmitSaga),
    ])
    // yield takeEvery(getTaskHistory, runEmitSaga)
}
