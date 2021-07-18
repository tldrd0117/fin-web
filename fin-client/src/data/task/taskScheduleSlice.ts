import { createAction, createSlice } from "@reduxjs/toolkit";


const taskScheduleSlice = createSlice({
    name: "taskSchedule",
    initialState: {
        list: [{
            id: "",
            year: "*",
            month: "*",
            day: "*",
            hour: "*",
            minute: "*",
            second: "0"
        }]
    },
    reducers:{
        fetchTaskScheduleRes: (state, action) => {
            const { payload } = action;
            state.list = payload.list
            console.log("fetchTaskScheduleRes", payload)
        },
    }
})

const { actions, reducer } = taskScheduleSlice

export interface AddTaskSchedulePayload{
    year: string
    month: string
    day: string
    hour: string
    minute: string
    second: string
    market: Array<string> 
    startDate: string 
    endDate: string 
    taskId: string
}

export interface FetchTaskSchedulePayload{
}
export interface RemoveTaskSchedulePayload{
    id: string
}

export const fetchTaskSchedule = createAction<FetchTaskSchedulePayload>("taskSchedule/fetchTaskSchedule");
export const addTaskSchedule = createAction<AddTaskSchedulePayload>("taskSchedule/addTaskSchedule");
export const removeTaskSchedule = createAction<RemoveTaskSchedulePayload>("taskSchedule/removeTaskSchedule");
export const { fetchTaskScheduleRes } = actions
export default reducer