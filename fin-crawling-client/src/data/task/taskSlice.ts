import { createAction, createSlice } from "@reduxjs/toolkit";

let timeTest = 0;

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
        fetchTaskState: (state, action) => {
            timeTest = Date.now()
            console.log("startTime:" + timeTest)
        },
        fetchTaskStateRes: (state, action) => {
            const { payload } = action;
            console.log("takeTime:" + (Date.now()-timeTest))
            /*
                res
                [ {stocks, years, market, taskId}...]

                ret: 0 (WAIT), 1 (SUCCESS), 2 (FAIL)
            */
            
            state.yearData = payload.yearData
            Object.keys(payload.yearData).forEach(taskId=>{
                Object.keys(payload.yearData[taskId]).forEach(market=>{
                    state.yearData[taskId][market].stocks = payload.yearData[taskId][market].stocks.map(v=>({
                        date: v.date,
                        count: 1,
                        level: (v.ret+1)
                    }));
                    state.yearData[taskId][market].yearArray = Object.keys(payload.yearData[taskId][market].years).sort((a,b)=>Number(a)-Number(b))
                })

            })
        },
        updateTaskStateRes: (state, action) => {
            const { payload } = action;
            const { date, market, taskId, ret} = payload;
            const index = state.yearData[taskId][market].stocks.findIndex(v=> v.date == date);
            if(index == -1){
                state.yearData[taskId][market].stocks.push({
                    date, count: 1, level: (Number(ret)+1)
                })
                state.yearData[taskId][market].years[date.slice(0,4)] += 1
            } else {
                state.yearData[taskId][market].stocks[index] = {
                    date, count: 1, level: (Number(ret)+1)
                };
            }
            console.log(`updateRet: ${(Number(ret)+1)} ${date}`)
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

// export const fetchTaskState = createAction<FetchTaskPayload>("task/fetchTaskState");
export const { fetchTaskStateRes, fetchTaskState } = actions
export default reducer