import React from 'react'
import TaskProgressListItem from './TaskProgressListItem'
import LinearProgressBar from '../components/LinearProgressBar'
import { RootState } from '../data/root/rootReducer'
import { useSelector } from 'react-redux'


export default (props) => {
    const { taskId } = props
    const { tasks } = useSelector((state: RootState) => state.task.progress)
    if(tasks && tasks[taskId]){
        const { ids, list } = tasks[taskId]
        const allStates = ids && ids.length ? ids.reduce((acc, val) => {
            let state = list[val].state
            if(acc[state]){
                acc[state] += 1
            } else {
                acc[state] = 1
            }
            return acc
        },{}) : null
        return<>
            <div className='relative mt-4 mb-4'>
                <span>TaskCount: {ids? ids.length: "0"}</span>
            </div>
            <div className='relative mb-4'>
                {
                    allStates? Object.keys(allStates).map((state)=>{
                        return <span className={`relative inline-block rounded-full text-white
                            ${state=="running"?'bg-green-400 hover:bg-green-500':
                            state=="pending"?"bg-yellow-500 hover:bg-yellow-600":
                            state=="stop"?'bg-yellow-400 hover:bg-yellow-500':"bg-red-400 hover:bg-red-500"}
                                duration-300 
                            text-xs font-bold 
                            px-2 md:px-4 py-1 
                            opacity-90 hover:opacity-100 absolute top-0 right-0`}>
                            {`${state} ${allStates[state]}`||""}
                        </span>
                    }): null
                }
            </div>
            <div className={"relative"}>
                {
                    ids?ids.map(val=><TaskProgressListItem key={val} data={{...list[val], taskUniqueId: val}} />):
                    <div>Empty Task</div>
                }
            </div>
        </>
    } else {
        return <div></div>
    }
    
}