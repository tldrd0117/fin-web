import React from 'react'
import { useSelector } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import Card from '../components/Card';
import YearCalendar from '../components/YearCalendar';
import { RootState } from '../data/root/rootReducer';
import CrawlingCompleteList from './CrawlingCompleteList';
import CrawlingExecutionForm from './CrawlingExecutionForm';
import CrawlingForm from './CrawlingForm';
import CrawlingProgressList from './CrawlingProgressList';
import CrawlingSchedulingForm from './CrawlingSchedulingForm';
import CrawlingTaskScheduleList from './CrawlingTaskScheduleList'


export default (props) =>{
    const task = useSelector((state: RootState) => state.task)
    return <Card className={"mt-10 relative"}>
            <h2 className="text-gray-700 font-semibold text-xl sm:text-2xl tracking-wide mb-4 pr-10">일자별 주식 및 시가총액 크롤링</h2>
            <CrawlingExecutionForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p>Progress List</p>
            <CrawlingProgressList taskId={"marcap"}/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <CrawlingSchedulingForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p>Task Schedule</p>
            <CrawlingTaskScheduleList/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>

            <p className={"mt-2 mb-2"}>Task Calendar</p>
            {
                Object.keys(task.yearData["marcap"]).map(market=>{
                    return <>
                        <p>{market}</p>
                        <YearCalendar
                            blockSize={10} blockMargin={4}
                            fullYear={false}
                            style={{maxWidth:"100%"}}
                            task={task.yearData["marcap"][market]}
                            years={task.yearData["marcap"][market].yearArray}
                        >
                            <ReactTooltip delayShow={50} html />
                        </YearCalendar>
                    </>
                })
            }
            
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p className={"mt-2"}>Completed History</p>
            <CrawlingCompleteList taskId={"marcap"}/>
            
        </Card>

}