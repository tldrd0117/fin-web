import React from 'react'
import CrawlingProgressListItem from './CrawlingProgressListItem'
import LinearProgressBar from '../components/LinearProgressBar'
import { RootState } from '../data/root/rootReducer'
import { useSelector } from 'react-redux'
import HeaderTable from '../components/HeaderTable'


export default (props) => {
    const taskSchedule = useSelector((state: RootState) => state.taskSchedule)
    console.log("render: "+JSON.stringify(taskSchedule))
    return <div className={"relative"}>
        {
            taskSchedule.list.map(v=>
                <>
                <p className={"mt-2"}>{v.id}</p>
                <HeaderTable
                    header={[["년","월","일","시","분","초"]]}
                    body={[[v.year,v.month,v.day,v.hour,v.minute,v.second]]}
                />
                <HeaderTable
                    header={[["작업번호","시장","시작날짜","종료날짜"]]}
                    body={[...v.taskList.map((v,i)=>{
                        return [i,v.market,v.startDateStr, v.endDateStr]
                    })]}
                />
                </>
            )
        }
    </div>
    
}