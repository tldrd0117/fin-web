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
                <span className={'w-p'}>{startDateStr}</span>
                <span className={'w-p'}>{endDateStr}</span>
                <span className={'w-p'}>{market}</span>
                <span className={'w-p'}>{count}</span>
                <span className={'w-p'}>{successCount}</span>
                <span className={'w-p'}>{failCount}</span>
                <span className={'w-p'}>{percent}</span>
            </div>
        </>
}