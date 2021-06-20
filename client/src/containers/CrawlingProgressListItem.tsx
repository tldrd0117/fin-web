import React from 'react'
import LinearProgressBar from '../components/LinearProgressBar'

export default (props) => {
    const {
        data:{
            count,
            successCount,
            restCount,
            failCount,
            state,
            percent
        }
    } = props
    return <>
            <div className={"relative mt-4"}>
                <div>
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
            </div>
        </>
}