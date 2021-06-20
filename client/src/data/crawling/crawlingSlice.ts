import { createAction, createSlice } from "@reduxjs/toolkit";

const initialState = {
    tasks:{
        "marcap":{
            type:"marcap",
            list:{
                "0":{
                    id: 0,
                    count: 0,
                    successCount: 0,
                    restCount: 0,
                    failCount: 0,
                    percent: 0,
                    state: "stop"
                },
            },
            ids:[0]
        }
    },
    taskIds:["marcap"],
}

const crawlingSlice = createSlice({
    name: "crawling",
    initialState,
    reducers:{
        reset: (state, action) => {
            return initialState
        },
        runCrawling: (state, action) => {
            const { payload } = action
            const { market, startDate, endDate, taskId } = payload
            const id = taskId + market + startDate + endDate + Math.floor(Date.now() * Math.random())
            payload.id = id
            if(!state.tasks[taskId]){
                state.tasks[taskId] = {}
            }
            if(!state.tasks[taskId].list){
                state.tasks[taskId].list = {}
            }
            if(!state.tasks[taskId].ids){
                state.tasks[taskId].ids = []
            }
            state.tasks[taskId].list[id] = {...payload, id, state:"pending" }
            state.tasks[taskId].ids.push(id)
        },
        fetchTasksRes: (state, action) => {
            const { payload } = action;
            const { tasks, taskIds } = payload
            state.tasks = tasks
            state.taskIds = taskIds
        },
        runCrawlingRes: (state, action) => {
            const { payload } = action;
            const { tasks, taskIds } = payload
            state.tasks = tasks
            state.taskIds = taskIds
        }
    },
})

const { actions, reducer } = crawlingSlice
export const { runCrawling, fetchTasksRes, reset } = actions
export const fetchTasks = createAction<any>("crawling/fetchTasks")

export default reducer