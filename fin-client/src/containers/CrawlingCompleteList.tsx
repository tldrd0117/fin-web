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
            <style jsx>{`
                .w-p{
                    width: 14.2%;
                    text-align: center;
                }
            `}</style>
            <div className={"flex mt-4 h-10 items-center justify-between h-auto flex-wrap"}>
                <div className={'w-p flex-grow'}>
                    <div>시작날짜</div>
                    <div>종료날짜</div>
                </div>
                <span className={'w-p'}>시장</span>
                <span className={'w-p'}>전체</span>
                <span className={'w-p'}>성공</span>
                <span className={'w-p'}>실패</span>
                <span className={'w-p'}>퍼센트</span>
            </div>
            {
                ids?ids.map(val=><CrawlingCompleteListItem key={val} data={list[val]} />):null
            }
        </div>
    } else {
        return <div></div>
    }
    
}