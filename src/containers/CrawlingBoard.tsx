import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Breadcrumb from '../components/Breadcrumb';
import { fetchCompletedTask } from '../data/crawling/crawlingHistorySlice';
import { RootState } from '../data/root/rootReducer';
import { fetchTaskSchedule } from '../data/task/taskScheduleSlice';
import { fetchTaskState } from '../data/task/taskSlice';
import CrawlingList from './CrawlingList';

export default (props) => {
    const {isConnected} = useSelector((state: RootState)=>state.socket)
    const dispatch = useDispatch()
    useEffect(()=>{
        if(isConnected){
            dispatch(fetchCompletedTask({}))
            dispatch(fetchTaskState({ taskId: "marcap"}))
            dispatch(fetchTaskSchedule({}))
        }
    },[isConnected])
    
    return <>
        <style jsx>{`
            .container{
                @apply flex flex-col p-4 bg-gray-100;
                @apply overflow-auto;
            }
            :global(.playButton){
                top:30px;
                right:30px;
            }
        `}</style>
        <div className={"container"}>
            <Breadcrumb data={[{
                link:"#",
                name:"fin-crawling"
            },{
                name:"일자별 주식 및 시가총액"
            }]}/>
            <CrawlingList/>
            
        </div>
    </>
}