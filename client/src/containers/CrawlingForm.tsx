import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import DatePicker from '../components/DatePicker'
import PlayButton from '../components/PlayButton'
import { runCrawling } from '../data/crawling/crawlingSlice'
import { getDateString } from '../utils/DateUtils'
import colors from 'tailwindcss/colors'

export default (props) => {
    const [startDate, setStartDate] = useState(new Date())
    const [endDate, setEndDate] = useState(new Date())
    const dispatch = useDispatch()
    const handleButton = () => {
        dispatch(
            runCrawling({
                taskId: "marcap",
                market:"kospi",
                startDate: getDateString(startDate),
                endDate: getDateString(endDate),
            })
        )
        console.log(getDateString(startDate), getDateString(endDate))
    }
    
    return <>
        <h2 className="text-gray-700 font-semibold text-2xl tracking-wide mb-4">일자별 주식 및 시가총액 크롤링</h2>
        <label className="block text-gray-400 text-sm font-bold mb-2" >
            날짜
        </label>
        <div className={"flex items-center"}>
            <DatePicker className={"mr-3 focus:ring-4"} selected={startDate} onChange={date=> setStartDate(date)}/>
            ~
            <DatePicker className={"ml-3 focus:ring-4"} selected={endDate} onChange={date => setEndDate(date)}/>
            <PlayButton className={"absolute top-8 right-8"} onClick={handleButton} iconColor={colors.emerald[100]}/>
        </div>
    </>
}