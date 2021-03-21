import React, { useState } from 'react';

interface OutLineTextField{

}

export default (props) => {
    const height = 40;
    return <>
        <style jsx>{`
            input{
                height: ${height}px;
                margin-top: 4px;
                @apply px-3;
            }
            label{
                left: 20px;
                top: ${height/2-11}px;
                background-color: white;
                transition: 0.3s;
                padding: 3px;
                box-sizing: border-box;
                
            }
            input:focus + label{
                left: 20px;
                top: -5px;
                font-size: 5px;
                @apply text-blue-500;
            }
        `}</style>
        <div className={`relative ${props.className?props.className : ""}`}>
            <input type={"text"} className={`border-solid border border-light-blue-500 w-full`}/>
            <label className={"label absolute text-gray-400"}>{props.label}</label>
        </div>
    </>
}