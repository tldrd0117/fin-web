import React from 'react'
import Card from '../components/Card'
import FactorFileExecutionForm from './FactorFileExecutionForm'
import ToggleTitle from './ToggleTitle'

export default () => {
    return <>
        <Card className={"mt-10 relative"}>
            <h2 className="text-gray-700 font-semibold text-xl sm:text-2xl tracking-wide mb-4 pr-10">팩터 파일에서 가져오기</h2>
            <FactorFileExecutionForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p>Progress List</p>
            {/* <CrawlingProgressList taskId={"marcap"}/> */}
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            {/* <CrawlingSchedulingForm/> */}
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <ToggleTitle
                title={"Task List"}
                show={
                    <>
                        {/* <CrawlingTaskScheduleList/> */}
                    </>
                }
                hide={null}/>
            <div className={"w-full h-px bg-gray-300 mt-4 mb-4"}></div>
            
            
        </Card>
    </>
}