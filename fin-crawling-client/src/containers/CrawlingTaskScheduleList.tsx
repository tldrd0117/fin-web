import React from 'react'
import CrawlingProgressListItem from './TaskProgressListItem'
import LinearProgressBar from '../components/LinearProgressBar'
import { RootState } from '../data/root/rootReducer'
import { useDispatch, useSelector } from 'react-redux'
import HeaderTable from '../components/HeaderTable'
import Button from '../components/Button'
import { removeTaskSchedule } from '../data/task/taskScheduleSlice'


export default (props) => {
    const taskSchedule = useSelector((state: RootState) => state.task.schedule)
    const dispatch = useDispatch()
    const handleRemove = (id: string) => {
        dispatch(removeTaskSchedule({
            id
        }))
    }
    return <div className={"relative"}>
        {
            taskSchedule.list && taskSchedule.list.length > 0?
            taskSchedule.list.map(v=>
                <>
                    <p className={"mt-2"}>{v.id}</p>
                    <HeaderTable
                        header={[["년","월","일","시","분","초"]]}
                        body={[[v.year, v.year,v.month,v.day,v.hour,v.minute,v.second]]}
                    />
                    <HeaderTable
                        header={[["작업번호","시장","시작날짜","종료날짜"]]}
                        body={[...v.taskList.map((v,i)=>{
                            return [i, i,v.market,v.startDateStr, v.endDateStr]
                        })]}
                    />
                    <Button onClick={() => handleRemove(v.id)} className={"bg-red-400 hover:bg-red-500 text-white text-sm mt-4"}>삭제</Button>
                </>
            ):
            <p>데이터가 없습니다.</p>
        }
    </div>
    
}