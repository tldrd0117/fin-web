import React from 'react';
import MenuIcon from '../components/MenuIcon';

export default (props) => {
    const {children, className, title, onMenuIconClick} = props;
    return <>
        <style jsx>{`
            .title{
                padding: 30px;
                margin: 0px;
            }
        `}</style>
        <div className={`flex items-center shadow-lg ${className?className:""}`}>
            <MenuIcon
                className={"ml-2 sm:hidden hover:bg-blue-500 hover:bg-opacity-30 rounded-full w-10 h-10 flex items-center justify-center"}
                onClick={onMenuIconClick}/>
            <label className={"title"}>{title?title:""}</label>
            {children}
        </div>
    </>
}