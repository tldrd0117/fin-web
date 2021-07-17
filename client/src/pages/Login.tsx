import React from 'react';
import LoginBox from '../containers/LoginBox';
import YearCalendar from '../components/YearCalendar'
import ReactTooltip from 'react-tooltip'

export default () => {
    return <>
        <div
            className={"absolute w-full h-full flex flex-col items-center justify-center"}
            >
            <LoginBox/>
        </div>
        
    </>
}