import React from 'react'
import { useSelector } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import Card from '../components/Card';
import YearCalendar from '../components/YearCalendar';
import { RootState } from '../data/root/rootReducer';
import CrawlingCompleteList from './CrawlingCompleteList';
import CrawlingForm from './CrawlingForm';
import CrawlingProgressList from './CrawlingProgressList';
import CrawlingTaskScheduleList from './CrawlingTaskScheduleList'


export default (props) =>{
    const task = useSelector((state: RootState) => state.task)
    return <Card className={"mt-10 relative"}>
            <CrawlingForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p>Task Schedule</p>
            <CrawlingTaskScheduleList/>
            <p>Progress List</p>
            <CrawlingProgressList taskId={"marcap"}/>

            <p className={"mt-2 mb-2"}>Task Calendar</p>
            <YearCalendar
                blockSize={10} blockMargin={4}
                fullYear={false}
                style={{maxWidth:"100%"}}
                task={task}
                years={task.yearArray}
            >
                <ReactTooltip delayShow={50} html />
            </YearCalendar>
            
            <p className={"mt-2"}>Completed History</p>
            <CrawlingCompleteList taskId={"marcap"}/>
            
        </Card>

}