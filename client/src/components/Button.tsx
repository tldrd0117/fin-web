import React, { MouseEventHandler } from 'react';

interface ButtonProps{
    children?: React.ReactNode
    onClick?: MouseEventHandler
    className?: string
}

export default (props: ButtonProps) => {
    const {children, onClick} = props;
    return <>
        <style jsx>{`
        `}</style>
        <button onClick={onClick} className={`focus:outline-none text-white text-sm py-2.5 px-5 rounded-md bg-blue-500 hover:bg-blue-600 hover:shadow-lg ${props.className?props.className : ""}`}>
            {children}
        </button>
    </>
}