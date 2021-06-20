import React from 'react'
import CrawlingProgressListItem from './CrawlingProgressListItem'
import LinearProgressBar from '../components/LinearProgressBar'
import { RootState } from '../data/root/rootReducer'
import { useSelector } from 'react-redux'


export default (props) => {
    const { taskId } = props
    const { tasks } = useSelector((state: RootState) => state.crawling)
    if(tasks && tasks[taskId]){
        const { ids, list } = tasks[taskId]
        return <div className={"relative"}>
            {
                ids?ids.map(val=><CrawlingProgressListItem key={val} data={list[val]} />):null
            }
        </div>
    } else {
        return <div></div>
    }
    
}