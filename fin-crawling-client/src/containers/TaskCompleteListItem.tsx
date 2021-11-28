import React from 'react'
import LinearProgressBar from '../components/LinearProgressBar'
import { getDateHipen } from '../utils/DateUtils';

export default (props) => {
    const {
        data:{
            count,
            successCount,
            restCount,
            failCount,
            state,
            percent,
            startDateStr,
            endDateStr,
            market
        }
    } = props
    return <>
            <style jsx>{`
                .w-p{
                    width: 14.2%;
                    text-align: right;
                }
            `}</style>
            
            <div className={"flex mt-4 h-10 items-center justify-between h-auto flex-wrap"}>
                <div className={'w-p flex-grow'}>
                    <div>{startDateStr}</div>
                    <div>{endDateStr}</div>
                </div>
                <div className={'w-p'}>{market}</div>
                <div className={'w-p'}>{count}</div>
                <div className={'w-p'}>{successCount}</div>
                <div className={'w-p'}>{failCount}</div>
                <div className={'w-p'}>{percent}</div>
            </div>
        </>
}