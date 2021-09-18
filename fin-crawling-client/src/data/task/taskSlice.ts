import { createAction, createSlice } from "@reduxjs/toolkit";


const taskSlice = createSlice({
    name: "task",
    initialState: {
        yearData: {
            marcap:{
                kospi:{
                    stocks: [],
                    years:{},
                    yearArray:[],
                },
                kosdaq:{
                    stocks: [],
                    years:{},
                    yearArray:[],
                }
            }
        },
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
            /*
                res
                [ {stocks, years, market, taskId}...]
            */
            
            state.yearData = payload
            Object.keys(payload).forEach(taskId=>{
                Object.keys(payload[taskId]).forEach(market=>{
                    state.yearData[taskId][market].stocks = payload[taskId][market].stocks.map(v=>({
                        date: v.date,
                        count: 1,
                        level: (v.ret+1)
                    }));
                    state.yearData[taskId][market].yearArray = Object.keys(payload[taskId][market].years).sort((a,b)=>Number(a)-Number(b))
                })

            })
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