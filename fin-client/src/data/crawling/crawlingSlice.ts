import { createAction, createSlice } from "@reduxjs/toolkit";

const initialState = {
    tasks:{
        "marcap":{
            type:"marcap",
            list:{
                "0":{
                    "id": 0,
                    "count": 5, 
                    "createdAt": "", 
                    "endDateStr": "20000000", 
                    "failCount": 0, 
                    "failTasks": [], 
                    "index": 5, 
                    "market": "kospi", 
                    "percent": 100.0, 
                    "restCount": 0, 
                    "startDateStr": "20000000", 
                    "state": "success", 
                    "successCount": 5, 
                    "taskId": "marcap", 
                    "tasks": ["20210701", "20210702", "20210703", "20210704", "20210705"], 
                    "tasksRet": [1, 1, 1, 1, 1], 
                    "updatedAt": ""
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
            const { taskId } = payload
            const id = Math.floor(Date.now() * Math.random())
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

interface RunCrawlingPayload{
    taskId: string
    market: Array<string>
    startDate: string
    endDate: string
}

interface CancelCrawlingPayload{
    taskId: string
    market: Array<string>
    startDate: string
    endDate: string
    taskUniqueId: string
}

const { actions, reducer } = crawlingSlice
export const { runCrawling, fetchTasksRes, reset } = actions
export const cancelCrawling = createAction<CancelCrawlingPayload>("crawling/cancelCrawling")
export const fetchTasks = createAction<RunCrawlingPayload>("crawling/fetchTasks")

export default reducer