import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import DatePicker from '../components/DatePicker'
import PlayButton from '../components/PlayButton'
import { runCrawling } from '../data/crawling/crawlingSlice'
import { addTaskSchedule } from '../data/task/taskScheduleSlice'
import { getDateString } from '../utils/DateUtils'
import colors from 'tailwindcss/colors'
import OutLineTextField from '../components/OutLineTextField'
import Button from '../components/Button'
import CheckBox from '../components/CheckBox'
import Select from 'react-select'

export default (props) => {

    const dispatch = useDispatch()
    const handleRunCrawlingButton = () => {
        console.log("play")
        // dispatch(
        //     runCrawling({
        //         taskId: "marcap",
        //         market,
        //         startDate: getDateString(startDate),
        //         endDate: getDateString(endDate),
        //     })
        // )
        // console.log(market, getDateString(startDate), getDateString(endDate))
    }
    
    return <>
        <div className={"flex items-center justify-between mb-2"}>
            <label className="block text-black text-medium font-semibold" >
                실행
            </label>
            <PlayButton className={""} onClick={handleRunCrawlingButton} iconColor={colors.emerald[100]}/>
        </div>
        
    </>
}