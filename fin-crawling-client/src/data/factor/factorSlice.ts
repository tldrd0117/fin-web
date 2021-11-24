import { createAction, createSlice } from "@reduxjs/toolkit";

const initialState = {
    tasks:{
        "factorFile":{
            type:"factorFile",
            list:{
                "0":{
                    "id": 0,
                    "count": 5, 
                    "createdAt": "", 
                    "endDateStr": "20000000", 
                    "failCount": 0, 
                    "failTasks": [], 
                    "index": 5, 
                    "percent": 100.0, 
                    "restCount": 0, 
                    "startDateStr": "20000000", 
                    "state": "success", 
                    "successCount": 5, 
                    "taskId": "factorFile", 
                    "tasks": [""], 
                    "tasksRet": [1, 1, 1, 1, 1], 
                    "updatedAt": ""
                },
            },
            ids:[0]
        }
    },
    taskIds:["factorFile"],
}

const crawlingSlice = createSlice({
    name: "factor",
    initialState,
    reducers:{
        convertFileToDb: (state, action) => {
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
        convertFileToDbStartRes: (state, action) => {
            const { payload } = action;
            const { tasks, taskIds } = payload
            state.tasks = tasks
            state.taskIds = taskIds
            console.log("convertFileToDbStartRes")
        },
        convertFileToDbEndRes: (state, action) => {
            const { payload } = action;
            const { tasks, taskIds } = payload
            state.tasks = tasks
            state.taskIds = taskIds
            console.log("convertFileToDbEndRes")
        },
        fetchTasksRes: (state, action) => {
            const { payload } = action;
            const { tasks, taskIds } = payload
            state.tasks = tasks
            state.taskIds = taskIds
            console.log("fetchTasksRes")
        },
        fetchCompletedTaskRes: (state, action) => {
            const { payload } = action;
            const { tasks, taskIds } = payload
            state.tasks = tasks
            state.taskIds = taskIds
            console.log("fetchCompletedTaskRes")
        },
    },
})

interface ConvertFileToDbPayload{
    taskId: string
}

export const fetchCompletedTask = createAction<any>("factor/fetchCompletedTask")

const { actions, reducer } = crawlingSlice
export const { convertFileToDb, convertFileToDbStartRes, convertFileToDbEndRes, fetchTasksRes, fetchCompletedTaskRes } = actions

export default reducer