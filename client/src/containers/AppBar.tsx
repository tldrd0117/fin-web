import React from 'react';

export default (props) => {
    const {children, className, title} = props;
    return <>
        <style jsx>{`
            .title{
                padding: 30px;
            }
        `}</style>
        <div className={`flex items-center shadow-lg ${className?className:""}`}>
            <label className={"title"}>{title?title:""}</label>
            {children}
        </div>
    </>
}