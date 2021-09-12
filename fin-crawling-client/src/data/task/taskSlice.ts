import { createAction, createSlice } from "@reduxjs/toolkit";


const taskSlice = createSlice({
    name: "task",
    initialState: {
        stocks: [],
        years:{},
        yearArray:[],
        poolInfo: {
            poolSize: 0,
            poolCount: 0,
            runCount: 0,
            queueCount: 0
        }
    },
    reducers:{
        fetchTaskStateRes: (state, action) => {
            const { payload } = action;
            state.stocks = payload.stocks.map(v=>({
                date: v.date,
                count: 1,
                level: (v.ret+1)
            }));
            state.years = payload.years;
            state.yearArray = Object.keys(payload.years).sort((a,b)=>Number(a)-Number(b))

        },
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

export const fetchTaskState = createAction<FetchTaskPayload>("task/fetchTaskState");
export const { fetchTaskStateRes } = actions
export default reducer