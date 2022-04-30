import React from 'react';
import JoinBox from '../containers/JoinBox';
import YearCalendar from '../components/YearCalendar'
import ReactTooltip from 'react-tooltip'

export default () => {
    return <>
        <div
            className={"absolute w-full h-full flex flex-col items-center justify-center"}
            >
            <JoinBox/>
        </div>
        
    </>
}