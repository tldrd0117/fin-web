import React, { useState } from 'react';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
// https://reactdatepicker.com/

export default (props) => {
    const [startDate, setStartDate] = useState(new Date());
    return <>
        <style jsx global>{`
            .datepicker{
                width: 120px;
            }
        `}</style>
        <DatePicker 
            className={`border-solid border border-light-blue-500 px-4 h-10 datepicker ${props.className?props.className : ""}`}
            dateFormat="yyyy/MM/dd"
            selected={startDate} 
            onChange={date => setStartDate(date)} />
    </>
}