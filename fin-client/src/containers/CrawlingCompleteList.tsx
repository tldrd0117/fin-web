import React from 'react'
import { RootState } from '../data/root/rootReducer'
import { useDispatch, useSelector } from 'react-redux'
import CrawlingCompleteListItem from './CrawlingCompleteListItem'
import HeaderTable from '../components/HeaderTable'
import { fetchCompletedTask } from '../data/crawling/crawlingHistorySlice'


export default (props) => {
    const { taskId } = props
    const histData = useSelector((state: RootState) => state.crawlingHistory)
    const { data, offset, limit, count } = histData
    const dispatch = useDispatch()

    const handleNext = () => {
        if( count > offset + limit ){
            dispatch(fetchCompletedTask({offset:offset+limit, limit}))
        }
    }
    if(data.history && data.history[taskId]){
        const { ids, list } = data.history[taskId]
        return <div className={"relative"}>
            <style jsx>{`
                .w-p{
                    width: 14.2%;
                    text-align: center;
                }
            `}</style>
            <HeaderTable
                header={[["시작일자 ~ 종료일자","시장","전체","성공","실패","퍼센트"]]}
                body={[...ids.map(val=>{
                    const {
                        startDateStr,
                        endDateStr,
                        market,
                        count,
                        successCount,
                        failCount,
                        percent
                    } = list[val];
                    return [
                    `${startDateStr} ~ ${endDateStr}`, market, count, successCount, failCount, percent
                ]}), count <= offset + limit? null : <td onClick={handleNext} className={"text-center text-sm p-4"} colSpan={6}>더보기</td>]}
            />
        </div>
    } else {
        return <div></div>
    }
    
}