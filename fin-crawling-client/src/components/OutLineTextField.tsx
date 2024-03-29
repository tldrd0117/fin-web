import React, { ChangeEvent, ChangeEventHandler, useState, FocusEventHandler } from 'react';

interface OutLineTextFieldProps{
    className?: string
    value?: string
    onChange?: ChangeEventHandler<HTMLInputElement>,
    onBlur?: FocusEventHandler<HTMLInputElement>
    label?: string
    left?: number
}

export default (props: OutLineTextFieldProps) => {
    let height = 40;
    let top = height/2-11;
    let fontSize = 16;
    let left = 20;
    if(props.value && props.value.length> 0){
        top = -5
        fontSize = 5
    }
    if(props.left){
        left = props.left
    }
    return <>
        <style jsx>{`
            input{
                height: ${height}px;
                margin-top: 4px;
                @apply px-3;
            }
            label{
                left: ${left}px;
                top: ${top}px;
                background-color: white;
                transition: 0.3s;
                padding: 3px;
                box-sizing: border-box;
                font-size: ${fontSize}px;
                pointer-events: none;
            }
           
            input:focus + label{
                left: ${left}px;
                top: -5px;
                font-size: 5px;
                @apply text-blue-500;
            }
            
        `}</style>
        <div className={`relative ${props.className?props.className : ""}`}>
            <input value={props.value}
                onBlur={props.onBlur}
                onChange={props.onChange} 
                type={"text"} 
                className={`border-solid border border-light-blue-500 w-full`}/>
            <label className={"select-none pointer-events-none label absolute text-gray-400"}>{props.label}</label>
        </div>
    </>
}