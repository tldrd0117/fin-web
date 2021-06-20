import { createAction, createSlice } from "@reduxjs/toolkit";

const crawlingSlice = createSlice({
    name: "crawling",
    initialState: {
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
    },
    reducers:{
        fetchCompletedTaskRes: (state, action) => {
            const { payload } = action;
            const { history, historyIds } = payload
            state.history = history
            state.historyIds = historyIds
        }
    },
})

const { actions, reducer } = crawlingSlice
export const { fetchCompletedTaskRes } = actions
export const fetchCompletedTask = createAction<any>("crawling/fetchCompletedTask")

export default reducer