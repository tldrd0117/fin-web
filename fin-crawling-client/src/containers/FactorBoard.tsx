import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Breadcrumb from '../components/Breadcrumb';
import { RootState } from '../data/root/rootReducer';
import { fetchTaskSchedule } from '../data/task/taskScheduleSlice';
import { fetchTaskState } from '../data/task/taskCalendarSlice';
import CrawlingList from './CrawlingList';
import FactorList from './FactorList';

export default (props) => {
    const {isConnected} = useSelector((state: RootState)=>state.socket)
    const dispatch = useDispatch()
    useEffect(()=>{
        if(isConnected){
            // dispatch(fetchCompletedTask({offset:0, limit:20}))
            // dispatch(fetchTaskState({ taskId: "marcap"}))
            // dispatch(fetchTaskSchedule({}))
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
                name:"팩터"
            }]}/>
            <FactorList/>
            
        </div>
    </>
}