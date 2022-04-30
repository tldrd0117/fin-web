import React, { ChangeEvent, ChangeEventHandler, useEffect, useRef, useState } from 'react';
import { FieldHookConfig, useField } from 'formik';


interface OutLineTextFieldProps{
    className?: string
    value?: string
    onChange?: ChangeEventHandler<HTMLInputElement>,
    label?: string
}

export default ({label, height = 40, wrapperClassName, formik, ...props}) => {
    let top = (height/2)-11;
    let fontSize = 16;
    const first = useRef(null)
    const [isEmpty, setEmpty] = useState(true);
    const [isFocus, setFocus] = useState(false);
    const [field, meta] = useField(props as FieldHookConfig<any>)
    const handleChange = (e) => {
        console.log("change")
        setEmpty(e.target.value.length == 0)
        formik.handleChange(e)
    }
    const handleFocus = (e) => {
        setFocus(true)
    }
    const handleBlur = (e) => {
        setFocus(false)
        formik.handleBlur(e)
    }

    const getLabelStyle = () => {
        const unfoldStyle = {
            top, fontSize
        }
        const foldStyle = {
            top : "-5px",
            fontSize : "5px"
        }
        if(isEmpty && !isFocus){
            return unfoldStyle
        } else {
            return foldStyle
        }
    }

    useEffect( () => {
        if(first && first.current){
            if(first.current.value && first.current.value.length > 0){
                setEmpty(false)
            } else {
                setEmpty(true)
            }
        }
    },[first])

    return <>
        <style jsx>{`
            input{
                margin-top: 4px;
            }
            label{
                left: 20px;
                background-color: white;
                transition: 0.3s;
                padding: 3px;
                box-sizing: border-box;
            }
            .focusClass{
                left: 20px;
                top: -5px;
                font-size: 5px;
            }
        `}</style>
        <div className={`relative ${wrapperClassName?wrapperClassName : ""}`}>
            <input {...props} {...field} 
                onChange={handleChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                onPaste={handleChange}
                value={formik.values[props.name]}
                className={`border-solid border border-light-blue-500 w-full px-3 ring-transparent`}
                style={{height}}
                ref={first}
            />
            <label htmlFor={props.id || props.name} 
                style={getLabelStyle()}
                className={`select-none pointer-events-none absolute text-gray-400 ${isFocus?"text-blue-500 focusClass":""}`}>{label}</label>
            {meta.touched && meta.error ? (
                <div className="text-sm text-red-500 mt-2">{meta.error}</div>
            ) : ""}
        </div>
    </>
}