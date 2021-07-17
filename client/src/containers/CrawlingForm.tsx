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
    const [startDate, setStartDate] = useState(new Date())
    const [endDate, setEndDate] = useState(new Date())
    const [reservedStartDate, setReservedStartDate] = useState(new Date())
    const [reservedEndDate, setReservedEndDate] = useState(new Date())
    const [isReservedDateFix, setReservedDateFix] = useState(false)

    const [year, setYear] = useState("*")
    const [month, setMonth] = useState("*")
    const [day, setDay] = useState("*")
    const [hour, setHour] = useState("*")
    const [minute, setMinute] = useState("*")
    const [second, setSecond] = useState("*")

    const [market, setMarket] = useState(["kospi"])
    const [reservedMarket, setReservedMarket] = useState(["kospi"])

    const dispatch = useDispatch()
    const handleRunCrawlingButton = () => {
        
        dispatch(
            runCrawling({
                taskId: "marcap",
                market,
                startDate: getDateString(startDate),
                endDate: getDateString(endDate),
            })
        )
        console.log(market, getDateString(startDate), getDateString(endDate))
    }

    const handleScheduleButton = () => {
        const startDate = isReservedDateFix?"*":getDateString(reservedStartDate)
        const endDate = isReservedDateFix?"*":getDateString(reservedEndDate)
        dispatch(
            addTaskSchedule({
                year, month, day, hour, minute, second,
                taskId: "marcap",
                market: reservedMarket,
                startDate,
                endDate
            })
        )
    }

    const hanldeReservedDateCheck = (isCheck: boolean) => {
        setReservedDateFix(isCheck)
    }

    const handleMarketChange = (arr) => {
        setMarket(arr.map(v=>v.value))
    }

    const handleMarketChangeOnReserved = (arr) => {
        setReservedMarket(arr.map(v=>v.value))
    }
    
    return <>
        <h2 className="text-gray-700 font-semibold text-xl sm:text-2xl tracking-wide mb-4 pr-10">일자별 주식 및 시가총액 크롤링</h2>
        
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
        <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
        <div className={"flex items-center justify-between mb-2"}>
            <label className="block text-black text-medium font-semibold" >
                예약실행
            </label>
            <PlayButton className={""} onClick={handleScheduleButton} iconColor={colors.emerald[100]}/>
        </div>
        <label className="block text-gray-400 text-sm font-bold mb-2" >
            주식시장
        </label>
        <Select
            defaultValue={{value:"kospi", label:"코스피"}}
            isMulti
            name="colors"
            options={[
                {value:"kospi", label:"코스피"},
                {value:"kosdaq", label:"코스닥"},
                {value:"konex", label:"코넥스"},
            ]}
            placeholder={"선택"}
            onChange={handleMarketChangeOnReserved}
            className={"basic-multi-select w-full sm:w-80 mb-2 "}
            classNamePrefix="select"
        />
        <div className={"flex flex-col"}>
            <label className="block text-gray-400 text-sm font-bold mb-2" >
                일자
            </label>
            <CheckBox checked={isReservedDateFix} onCheck={hanldeReservedDateCheck} className={"mb-2"} label={"예약일자로 고정"} />
            {
                isReservedDateFix?null:
                <div className={"flex items-center mb-4"}>
                <DatePicker 
                    className={"mr-3 focus:ring-4 w-28 sm:w-32 text-sm sm:text-base"} 
                    selected={reservedStartDate} 
                    onChange={date=> setReservedStartDate(date)}/>
                ~
                <DatePicker 
                    className={"ml-3 focus:ring-4 w-28 sm:w-32 text-sm sm:text-base"} 
                    selected={reservedEndDate} onChange={date => 
                    setReservedEndDate(date)}/>
            </div>
            }
            
        </div>
        
        <label className="block text-gray-400 text-sm font-bold mb-2" >
            예약일자
        </label>
        <div className={"flex items-center flex-wrap"}>
            <OutLineTextField value={year} onChange={(e)=>setYear(e.target.value)} className={"mr-1 w-24"} left={10} label={"년"}/>
            <OutLineTextField value={month} onChange={(e)=>setMonth(e.target.value)} className={"mx-1 w-14"} left={10} label={"월"}/>
            <OutLineTextField value={day} onChange={(e)=>setDay(e.target.value)} className={"mx-1 w-14"} left={10} label={"일"}/>
            <OutLineTextField value={hour} onChange={(e)=>setHour(e.target.value)} className={"mx-1 w-14"} left={10} label={"시"}/>
            <OutLineTextField value={minute} onChange={(e)=>setMinute(e.target.value)} className={"mx-1 w-14"} left={10} label={"분"}/>
            <OutLineTextField value={second} onChange={(e)=>setSecond(e.target.value)} className={"ml-1 w-14"} left={10} label={"초"}/>
        </div>
    </>
}