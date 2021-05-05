import React from 'react';

interface LinearProgressBarProps{
    className?: string;
    percent: number;
}

export default (props: LinearProgressBarProps) => {
    return <>
        <style jsx>{`
        `}</style>
        <div className={`w-full h-4 bg-gray-400 rounded-full mt-3 ${props.className?props.className : ""}`}>
            <div className="h-full text-center text-xs text-white bg-green-500 rounded-full" style={{width: props.percent+"%"}}>
            </div>
        </div>
    </>
}