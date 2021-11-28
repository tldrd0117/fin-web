import { createAction, createSlice } from "@reduxjs/toolkit";

let timeTest = 0;

const taskSlice = createSlice({
    name: "task/calendar",
    initialState: {
        data: {
            marcap:{
                kospi:{
                    stocks: [],
                    years:{},
                    yearArray:[],
                    lastUpdateYear: 2021
                },
                kosdaq:{
                    stocks: [],
                    years:{},
                    yearArray:[],
                    lastUpdateYear: 2021
                }
            }
        }
    },
    reducers:{
        //태스크 상태 새로 받기
        fetchTaskStateRes: (state, action) => {
            const { payload } = action;
            const loadedTime = Date.now()
            console.log("loadedTime:" + (loadedTime-timeTest))
            /*
                res
                [ {stocks, years, market, taskId}...]

                ret: 0 (WAIT), 1 (SUCCESS), 2 (FAIL)
            */
            
            state.data = payload.yearData
            Object.keys(payload.yearData).forEach(taskId=>{
                Object.keys(payload.yearData[taskId]).forEach(market=>{
                    state.data[taskId][market].stocks = payload.yearData[taskId][market].stocks.map(v=>({
                        date: v.date,
                        count: 1,
                        level: (v.ret+1)
                    }));
                    state.data[taskId][market].yearArray = Object.keys(payload.yearData[taskId][market].years).sort((a,b)=>Number(b)-Number(a))
                })

            })
            console.log("convertedTime:" + (Date.now()-loadedTime))
        },
        // 테스크 상태 갱신
        updateTaskStateRes: (state, action) => {
            const { payload } = action;
            const { date, market, taskId, ret} = payload;
            const index = state.data[taskId][market].stocks.findIndex(v=> v.date == date);
            if(index == -1){
                state.data[taskId][market].stocks.push({
                    date, count: 1, level: (Number(ret)+1)
                })
                state.data[taskId][market].years[date.slice(0,4)] += 1
            } else {
                state.data[taskId][market].stocks[index] = {
                    date, count: 1, level: (Number(ret)+1)
                };
                // state.yearData[taskId][market].years[date.slice(0,4)] = 0
                // state.yearData[taskId][market].yearArray
            }
            const count = state.data[taskId][market].years[date.slice(0,4)]
            if(count){
                state.data[taskId][market].years[date.slice(0,4)] += 1
            } else {
                state.data[taskId][market].years[date.slice(0,4)] = 1
            }
            const yearIndex = state.data[taskId][market].yearArray.findIndex(v=> v == date.slice(0,4));
            if(yearIndex == -1){
                state.data[taskId][market].yearArray.push(date.slice(0,4))
            }
            state.data[taskId][market].lastUpdateYear = date.slice(0,4)
            console.log(`updateRet: ${(Number(ret)+1)} ${date}`)
        }

    }
})

const { actions, reducer } = taskSlice

export interface FetchTaskPayload{
    taskId: string
}

export const fetchTaskState = createAction<FetchTaskPayload>("task/calendar/fetchTaskState");
export const { fetchTaskStateRes} = actions
export default reducer