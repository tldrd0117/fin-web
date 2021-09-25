import React, { useState } from 'react';
import Button from '../components/Button';

export default ({ title, show, hide, defaultValue=false}) => {
    const [isShow, setShow] = useState(defaultValue)
    const hanldeToggle = () => {
        setShow(!isShow)
    }
    return <>
        <style jsx>{`
        `}</style>
        <div className={"flex justify-between items-center"}>
            <p >{title}</p>
            <Button className={"bg-purple-500 text-white"} onClick={hanldeToggle}>{isShow?"닫기":"열기"}</Button>
        </div>
        {
            isShow? show : hide
        }
        
    </>
}
