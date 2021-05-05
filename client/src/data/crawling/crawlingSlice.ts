import { createAction, createSlice } from "@reduxjs/toolkit";

const crawlingSlice = createSlice({
    name: "crawling",
    initialState: {
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
        history:{
        },
        historyIds:[]
    },
    reducers:{
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
        updateTasks: (state, action) => {
            const { payload } = action;
            const { tasks, taskIds } = payload
            state.tasks = tasks
            state.taskIds = taskIds
        },
        updateTaskHistory: (state, action) => {
            const { payload } = action;
            const { history, historyIds } = payload
            state.history = history
            state.historyIds = historyIds
        }
    }
})

const { actions, reducer } = crawlingSlice
export const { runCrawling } = actions
export const getTaskHistory = createAction<any>("crawling/getTaskHistory")

export default reducer