import React from 'react'
import { RootState } from '../data/root/rootReducer'
import { useSelector } from 'react-redux'
import CrawlingCompleteListItem from './CrawlingCompleteListItem'


export default (props) => {
    const { taskId } = props
    const { history } = useSelector((state: RootState) => state.crawlingHistory)
    if(history && history[taskId]){
        const { ids, list } = history[taskId]
        return <div className={"relative"}>
            {
                ids?ids.map(val=><CrawlingCompleteListItem key={val} data={list[val]} />):null
            }
        </div>
    } else {
        return <div></div>
    }
    
}