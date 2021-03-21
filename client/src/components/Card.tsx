import React from 'react';

export default (props) => {
    const {children} = props;
    return <>
        <style jsx>{`
        `}</style>
        <div className={`shadow-sm ${props.className?props.className : ""}`}>
            {children}
        </div>
    </>
}