import { push } from 'connected-react-router';
import React from 'react';
import { useDispatch } from 'react-redux';
import MenuItem from '../components/MenuItem';

export default ({ menus, className = "", width="300px", onClick=null }) => {
    const dispatch = useDispatch()
    const handleClick = (url) => {
        console.log("handleClick")
        dispatch(push(`${url}`))
        if(onClick) onClick();
    }
    return <>
        <style jsx>{`
            .menu{
                width: ${width};
                height: 100%;
                overflow: auto;
                padding-top: 20px;
            }
        `}</style>
        <div className={`menu shadow bg-gray-700 flex flex-col ${className}`}>
            {menus.map(menu=><MenuItem onClick={()=>handleClick(menu.url)} key={menu.name}>{menu.name}</MenuItem>)}
        </div>
    </>
}
