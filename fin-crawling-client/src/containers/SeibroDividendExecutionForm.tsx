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
    const [startDate, setStartDate] = useState(new Date())
    const [endDate, setEndDate] = useState(new Date())
    const handleRunCrawlingButton = () => {
        console.log("play")
        dispatch(
            addTask({
                taskName: "SeibroDividendScrapService",
                taskId: "seibroDividend",
                startDate: getDateString(startDate),
                endDate: getDateString(endDate),
            })
        )
    }
    
    return <>
        <div className={"flex items-center justify-between mb-2"}>
            <label className="block text-black text-medium font-semibold" >
                실행
            </label>
            <PlayButton className={""} onClick={handleRunCrawlingButton} iconColor={colors.emerald[100]}/>
        </div>
        <label className="block text-gray-400 text-sm font-bold mb-2" >
            일자
        </label>
        <div className={"flex items-center"}>
            <DatePicker 
                className={"mr-3 focus:ring-4 w-28 sm:w-32 text-sm sm:text-base"} 
                selected={startDate} 
                onChange={date=> setStartDate(date)}/>
            ~
            <DatePicker 
                className={"ml-3 focus:ring-4 w-28 sm:w-32 text-sm sm:text-base"} 
                selected={endDate} 
                onChange={date => setEndDate(date)}/>
        </div>
        
    </>
}