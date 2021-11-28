import { createAction, createSlice } from "@reduxjs/toolkit";

const taskHistory = createSlice({
    name: "task/history",
    initialState: {
        offset: 0,
        count: 0,
        limit: 0,
        data:{
            history:{
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
            historyIds:["marcap"],
        }
    },
    reducers:{
        fetchCompletedTaskRes: (state, action) => {
            const { payload } = action;
            const { offset, limit, count, data } = payload
            state.offset = offset
            state.limit = limit
            state.count = count
            if(offset == 0){
                state.data = data
            } else {
                data.historyIds.forEach(col => {
                    if(!state.data.historyIds.includes(col)){
                        state.data.historyIds.push(col)
                    }
                });
                Object.keys(data.history).forEach(key => {
                    if(!state.data.history[key]){
                        state.data.history[key] = data.history[key]
                    } else {
                        data.history[key].ids.forEach(val=>{
                            if(!state.data.history[key].ids.includes(val)){
                                state.data.history[key].ids.push(val)
                                state.data.history[key].list[val] = data.history[key].list[val]
                            }
                        })
                        
                    }
                })
            }
        }
    },
})

const { actions, reducer } = taskHistory

export interface FetchCompletedTaskPayload{
    taskId: string
    offset: number
    limit: number
}

export const { fetchCompletedTaskRes } = actions
export const fetchCompletedTask = createAction<FetchCompletedTaskPayload>("task/history/fetchCompletedTask")

export default reducer