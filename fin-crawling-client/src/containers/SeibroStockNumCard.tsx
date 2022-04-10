import React from 'react'
import Card from '../components/Card'
import TaskProgressList from './TaskProgressList'
import SeibroStockNumExecutionForm from './SeibroStockNumExecutionForm'
import ToggleTitle from './ToggleTitle'
import TaskCompleteList from './TaskCompleteList'

export default () => {
    return <>
        <Card className={"mt-10 relative"}>
            <h2 className="text-gray-700 font-semibold text-xl sm:text-2xl tracking-wide mb-4 pr-10">발행주식수증감내역 가져오기</h2>
            <SeibroStockNumExecutionForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p>Progress List</p>
            <TaskProgressList taskId={"seibroStockNum"}/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            {/* <CrawlingSchedulingForm/> */}
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <ToggleTitle
                title={"Task List"}
                show={
                    <>
                        <TaskCompleteList taskId={"seibroStockNum"}/>
                    </>
                }
                hide={null}/>
            <div className={"w-full h-px bg-gray-300 mt-4 mb-4"}></div>
            
            
        </Card>
    </>
}