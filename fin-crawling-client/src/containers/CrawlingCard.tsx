import React, { useState } from 'react'
import { useSelector } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import Card from '../components/Card';
import Toggle from '../components/Toggle';
import YearCalendar from '../components/YearCalendar';
import { RootState } from '../data/root/rootReducer';
import CrawlingCompleteList from './CrawlingCompleteList';
import CrawlingExecutionForm from './CrawlingExecutionForm';
import CrawlingForm from './CrawlingForm';
import CrawlingProgressList from './CrawlingProgressList';
import CrawlingSchedulingForm from './CrawlingSchedulingForm';
import CrawlingTaskScheduleList from './CrawlingTaskScheduleList'
import ToggleTitle from './ToggleTitle';
import YearCalandarList from './YearCalandarList';


export default (props) =>{
    const yearData = useSelector((state: RootState) => state.task.yearData)
    return <Card className={"mt-10 relative"}>
            <h2 className="text-gray-700 font-semibold text-xl sm:text-2xl tracking-wide mb-4 pr-10">일자별 주식 및 시가총액 크롤링</h2>
            <CrawlingExecutionForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p>Progress List</p>
            <CrawlingProgressList taskId={"marcap"}/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <CrawlingSchedulingForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <ToggleTitle
                title={"Task Schedule"}
                show={
                    <>
                        <CrawlingTaskScheduleList/>
                    </>
                }
                hide={null}/>
            <div className={"w-full h-px bg-gray-300 mt-4 mb-4"}></div>
            <ToggleTitle 
                title={"Task Calendar"}
                show={
                    <>
                        <YearCalandarList yearData={yearData}/>
                        {/* {
                            Object.keys(yearData["marcap"]).map(market=>{
                                return <div className={"mt-4"}>
                                    <p className={"mt-4 mb-2"}>{market}</p>
                                    <YearCalendar
                                        key={market}
                                        blockSize={10} blockMargin={4}
                                        fullYear={false}
                                        market={market}
                                        style={{maxWidth:"100%"}}
                                        task={yearData["marcap"][market]}
                                        years={yearData["marcap"][market].yearArray}
                                    >
                                        <ReactTooltip delayShow={50} html />
                                    </YearCalendar>
                                </div>
                            })
                        } */}
                    </>
                } 
                hide={null}
            />
            
            
            <div className={"w-full h-px bg-gray-300 mt-4 mb-4"}></div>
            <ToggleTitle
                title={"Completed History"}
                show={<>
                    <CrawlingCompleteList taskId={"marcap"}/>
                </>}
                hide={null}
            />
            {/* <p className={"mt-2"}>Completed History</p> */}
            
            
        </Card>

}