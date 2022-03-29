import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import DatePicker from '../components/DatePicker'
import PlayButton from '../components/PlayButton'
import { convertFileToDb } from '../data/factor/factorSlice'
import { addTaskSchedule } from '../data/task/taskScheduleSlice'
import { getDateString } from '../utils/DateUtils'
import colors from 'tailwindcss/colors'
import OutLineTextField from '../components/OutLineTextField'
import Button from '../components/Button'
import CheckBox from '../components/CheckBox'
import Select from 'react-select'
import { addTask } from '../data/task/taskProgressSlice'

export default (props) => {

    const dispatch = useDispatch()

    const [apiKey, setApiKey] = useState("48a43d39558cf752bc8d8e52709da34569a80")
    const [startYear, setStartYear] = useState(new Date().getFullYear().toString())
    const [endYear, setEndYear] = useState(new Date().getFullYear().toString())

    const handleRunCrawlingButton = () => {
        if(apiKey.length <= 0){
            console.error("api키를 입력하시오")
            return;
        }
        if(Number(startYear) < 2015){
            console.error("시작년도는 2015년 부터 가능합니다")
            return;
        }
        if(Number(endYear) < 2015){
            console.error("종료년도를 2015년 부터 가능합니다")
            return;
        }
        console.log("play")
        dispatch(
            addTask({
                taskName: "factorDartScrapService",
                taskId: "factorDart",
                startYear,
                endYear,
                apiKey,
                isCodeNew: false
            })
        )
    }

    const handleApiChange = (value) => {
        setApiKey(value)
    }
    
    const handleStartYearChange = (value) => {
        setStartYear(value)
    }
    
    const handleEndYearChange = (value) => {
        setEndYear(value)
    }
    
    return <>
        <div className={"flex items-center justify-between mb-2"}>
            <label className="block text-black text-medium font-semibold" >
                실행
            </label>
            
            <PlayButton className={""} onClick={handleRunCrawlingButton} iconColor={colors.emerald[100]}/>
        </div>
        <label className="block text-gray-400 text-sm font-bold mb-2" >
            API키
        </label>
        <div className={"flex items-center flex-wrap"}>
            <OutLineTextField 
                onChange={(e)=>handleApiChange(e.target.value)} 
                value={apiKey} 
                className={"mr-1 w-96"} 
                left={10} 
                label={"API KEY"}/>
        </div>
        <label className="block text-gray-400 text-sm font-bold mb-2 mt-4" >
            시작년도
        </label>
        <div className={"flex items-center flex-wrap"}>
            <OutLineTextField 
                onChange={(e)=>handleStartYearChange(e.target.value)} 
                value={startYear} 
                className={"mr-1 w-24"} 
                left={10} 
                label={"startYear"}/>
        </div>
        <label className="block text-gray-400 text-sm font-bold mb-2 mt-4" >
            종료년도
        </label>
        <div className={"flex items-center flex-wrap"}>
            <OutLineTextField 
                onChange={(e)=>handleEndYearChange(e.target.value)} 
                value={endYear} 
                className={"mr-1 w-24"} 
                left={10} 
                label={"endYear"}/>
        </div>
        
    </>
}