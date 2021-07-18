import React from 'react'
import CrawlingProgressListItem from './CrawlingProgressListItem'
import LinearProgressBar from '../components/LinearProgressBar'
import { RootState } from '../data/root/rootReducer'
import { useSelector } from 'react-redux'


export default (props) => {
    const taskSchedule = useSelector((state: RootState) => state.taskSchedule)
    console.log("render:"+taskSchedule)
    return <div className={"relative"}>
        {
            taskSchedule.list.map(v=><p>{JSON.stringify(v)}</p>)
        }
    </div>
    
}