import React, { ChangeEvent, ChangeEventHandler, useState } from 'react';

interface OutLineTextFieldProps{
    className?: string
    value?: string
    onChange?: ChangeEventHandler<HTMLInputElement>,
    label?: string
}

export default (props: OutLineTextFieldProps) => {
    let height = 40;
    let top = height/2-11;
    let fontSize = 16;
    if(props.value.length> 0){
        top = -5
        fontSize = 5
    }
    return <>
        <style jsx>{`
            input{
                height: ${height}px;
                margin-top: 4px;
                @apply px-3;
            }
            label{
                left: 20px;
                top: ${top}px;
                background-color: white;
                transition: 0.3s;
                padding: 3px;
                box-sizing: border-box;
                font-size: ${fontSize}px;
            }
           
            input:focus + label{
                left: 20px;
                top: -5px;
                font-size: 5px;
                @apply text-blue-500;
            }
            
        `}</style>
        <div className={`relative ${props.className?props.className : ""}`}>
            <input value={props.value} onChange={props.onChange} type={"text"} className={`border-solid border border-light-blue-500 w-full`}/>
            <label className={"label absolute text-gray-400"}>{props.label}</label>
        </div>
    </>
}