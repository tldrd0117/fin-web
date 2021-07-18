import React from 'react';

export default (props) => {
    const {children} = props;
    return <>
        <style jsx>{`
        `}</style>
        <div className={`bg-white rounded-lg shadow block p-8 ${props.className?props.className : ""}`}>
            {children}
        </div>
    </>
}