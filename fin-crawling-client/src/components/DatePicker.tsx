import React, { useState } from 'react';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
// https://reactdatepicker.com/

interface DatePickerProps{
    onChange: Function
    selected: Date
    className?: string
    format?: string
}

export default (props: DatePickerProps) => {
    const { onChange, selected, className, format="yyyy-MM-dd"} = props;
    return <>
        <style jsx global>{`
            .datepicker{
            }
        `}</style>
        <DatePicker 
            className={`datepicker border border-gray-200 text-center py-3 leading-none 
            rounded-lg shadow-sm focus:outline-none focus:shadow-outline 
            text-gray-600 font-medium ${className?className : ""}`}
            dateFormat={format}
            selected={selected} 
            onChange={onChange} />
    </>
}