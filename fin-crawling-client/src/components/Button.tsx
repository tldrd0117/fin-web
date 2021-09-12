import React, { MouseEventHandler } from 'react';

interface ButtonProps{
    children?: React.ReactNode
    onClick?: MouseEventHandler
    className?: string
}

export default ({children = null, ...props}) => {
    return <>
        <style jsx>{`
        `}</style>
        <button {...props} className={`focus:outline-none py-2.5 px-5 rounded-md hover:shadow-lg ${props.className?props.className : ""}`}>
            {children}
        </button>
    </>
}