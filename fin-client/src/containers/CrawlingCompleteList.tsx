import React from 'react'
import { RootState } from '../data/root/rootReducer'
import { useSelector } from 'react-redux'
import CrawlingCompleteListItem from './CrawlingCompleteListItem'
import HeaderTable from '../components/HeaderTable'


export default (props) => {
    const { taskId } = props
    const { history } = useSelector((state: RootState) => state.crawlingHistory)
    if(history && history[taskId]){
        const { ids, list } = history[taskId]
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
                ]})]}
            />
        </div>
    } else {
        return <div></div>
    }
    
}