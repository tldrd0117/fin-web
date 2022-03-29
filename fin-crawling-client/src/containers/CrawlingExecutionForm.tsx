import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import DatePicker from '../components/DatePicker'
import PlayButton from '../components/PlayButton'
import { getDateString } from '../utils/DateUtils'
import colors from 'tailwindcss/colors'
import OutLineTextField from '../components/OutLineTextField'
import Button from '../components/Button'
import CheckBox from '../components/CheckBox'
import Select from 'react-select'
import { addTask } from '../data/task/taskProgressSlice'

export default (props) => {
    const [startDate, setStartDate] = useState(new Date())
    const [endDate, setEndDate] = useState(new Date())

    const [market, setMarket] = useState(["kospi"])

    const dispatch = useDispatch()
    const handleRunCrawlingButton = () => {
        dispatch(
            addTask({
                taskName: "marcapScrapService",
                taskId: "marcap",
                market,
                startDate: getDateString(startDate),
                endDate: getDateString(endDate),
            })
        )
        
        console.log(market, getDateString(startDate), getDateString(endDate))
    }

    const handleMarketChange = (arr) => {
        setMarket(arr.map(v=>v.value))
    }
    
    return <>
        <div className={"flex items-center justify-between mb-2"}>
            <label className="block text-black text-medium font-semibold" >
                실행
            </label>
            <PlayButton className={""} onClick={handleRunCrawlingButton} iconColor={colors.emerald[100]}/>
        </div>
        <label className="block text-gray-400 text-sm font-bold mb-2" >
            주식시장
        </label>
        <Select
            defaultValue={{value:"kospi", label:"코스피"}}
            isMulti
            placeholder={"선택"}
            name="colors"
            options={[
                {value:"kospi", label:"코스피"},
                {value:"kosdaq", label:"코스닥"},
                {value:"konex", label:"코넥스"},
            ]}
            onChange={handleMarketChange}
            className={"basic-multi-select w-full sm:w-80 mb-2 "}
            classNamePrefix="select"
        />
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