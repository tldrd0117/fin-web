import React, { MouseEventHandler, useRef, useState } from 'react';

export default ({label="", ...props }) => {
    const [checked, setChecked] = useState(props.checked)
    const checkRef = useRef(null)
    const handleClick = (...args) => {
        if(checkRef.current){
            if(args[0].target.tagName=="LABEL"){
                setChecked(!checkRef.current.checked)
            }else{
                setChecked(checkRef.current.checked)
            }
            if(props.onCheck) props.onCheck(!checked)
        }
        if(props.onClick) props.onClick(...args)
    }
    return <>
        <style jsx>{`
            .checkComponent{
                height: 24px;
                width: auto;
            }
            .checkBox{
                width: 24px;
                height: 24px;
            }
            .checkImage{
                width: 20px;
                height: 20px;
            }
            .label{

            }
        `}</style>
        <div {...props} onClick={handleClick} className={`relative flex checkComponent items-center ${props.className?props.className:""}`} >
            <input ref={checkRef} checked={checked} type={"checkbox"} className={`checkBox relative appearance-none h-6 w-6 border border-gray-300 rounded-md checked:bg-blue-600 checked:border-transparent focus:outline-none`} />
            {
                checked?
                <div className={"checkBox flex items-center justify-center absolute pointer-events-none"}>
                    <svg xmlns="http://www.w3.org/2000/svg" className="text-white checkImage" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                </div>:null
                
            }
            <label className={"ml-1 label text-gray-400 text-sm"}>{label}</label>
        </div>
    </>
}