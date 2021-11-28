import { createAction, createSlice } from "@reduxjs/toolkit";


const taskScheduleSlice = createSlice({
    name: "task/schedule",
    initialState: {
        list: [{
            id: "",
            year: "*",
            month: "*",
            dayOfWeek: "*",
            day: "*",
            hour: "*",
            minute: "*",
            second: "0",
            taskList: []
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
    dayOfWeek: string
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

export const fetchTaskSchedule = createAction<FetchTaskSchedulePayload>("task/schedule/fetchTaskSchedule");
export const addTaskSchedule = createAction<AddTaskSchedulePayload>("task/schedule/addTaskSchedule");
export const removeTaskSchedule = createAction<RemoveTaskSchedulePayload>("task/schedule/removeTaskSchedule");
export const { fetchTaskScheduleRes } = actions
export default reducer