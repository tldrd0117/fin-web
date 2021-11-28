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
        return <div className={"relative"}>
            {
                ids?ids.map(val=><TaskProgressListItem key={val} data={{...list[val], taskUniqueId: val}} />):null
            }
        </div>
    } else {
        return <div></div>
    }
    
}