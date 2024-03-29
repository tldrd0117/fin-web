import React from 'react'
import { useDispatch } from 'react-redux'
import Button from '../components/Button'
import LinearProgressBar from '../components/LinearProgressBar'
import { cancelTask } from '../data/task/taskProgressSlice'
import {getDateHipen} from '../utils/DateUtils'



const progressState = (taskId: string, value: string) => {
    console.log(taskId)
    if(taskId == "seibroDividend" || taskId == "seibroStockNum"){
        return value
    } else {
        return getDateHipen(value)
    }
}

export default (props) => {
    const dispatch = useDispatch()
    const {
        data:{
            count,
            createdAt, 
            endDateStr, 
            failCount, 
            failTasks, 
            index, 
            market, 
            percent, 
            restCount, 
            startDateStr, 
            state, 
            successCount, 
            taskId, 
            tasks, 
            tasksRet, 
            updatedAt,
            taskUniqueId
        },
    } = props

    const handleCancel = () => {
        dispatch(cancelTask({
            taskId,
            taskUniqueId,
        }))
    }
    return <>
            <div className={"relative mt-4"}>
                <label className="block text-black text-medium font-semibold  mt-4" >
                    {`${market} - (${getDateHipen(startDateStr)} ~ ${getDateHipen(endDateStr)})`}
                </label>
                <div>
                    <label className="block text-gray-400 text-sm font-bold mb-2 mt-2" >
                        현재진행: <span className="ml-2 font-bold"> {tasks&&tasks[index] ? `${progressState(taskId, tasks[index])}` : ""}</span>
                    </label>
                    <span>{`전체: ${count||"0"}`}</span>
                    <span className={"text-green-400 ml-2"}>{`성공: ${successCount||"0"}`}</span>
                    <span className={"text-red-400 ml-2"}>{`실패: ${failCount||"0"}`}</span>
                </div>
                <div className={"flex justify-between mt-2"}>
                    <span>{`${percent||"0"} %`}</span>
                    <span className={"ml-2"}>
                        <span className={"text-blue-400"}>{(successCount+failCount)||"0"}</span>/<span>{count||"0"}</span>
                    </span>
                </div>
                <LinearProgressBar percent={percent} className={"w-full"}/>
                <span className={`inline-block rounded-full text-white
                    ${state=="running"?'bg-green-400 hover:bg-green-500':
                    state=="pending"?"bg-yellow-500 hover:bg-yellow-600":
                    state=="stop"?'bg-yellow-400 hover:bg-yellow-500':"bg-red-400 hover:bg-red-500"}
                        duration-300 
                    text-xs font-bold 
                    px-2 md:px-4 py-1 
                    opacity-90 hover:opacity-100 absolute top-0 right-0`}>
                    {state||""}
                </span>
                <Button onClick={handleCancel} className={"bg-red-400 hover:bg-red-500 text-white text-sm mt-4"}>취소</Button>
            </div>
        </>
}