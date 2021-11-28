import { createAction, createSlice } from "@reduxjs/toolkit";

let timeTest = 0;

const taskSlice = createSlice({
    name: "task/poolInfo",
    initialState: {
        poolInfo: {
            poolSize: 0,
            poolCount: 0,
            runCount: 0,
            queueCount: 0
        }
    },
    reducers:{
        fetchTaskPoolInfoRes: (state, action) => {
            const { payload } = action;
            state.poolInfo = payload
        }
    }
})

const { actions, reducer } = taskSlice

export interface FetchTaskPayload{
    taskId: string
}

// export const fetchTaskState = createAction<FetchTaskPayload>("task/fetchTaskState");
export const { fetchTaskPoolInfoRes } = actions
export default reducer