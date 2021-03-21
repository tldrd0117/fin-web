import React from 'react';

export default (props) => {
    const {children, onClick} = props;
    return <>
        <style jsx>{`
        `}</style>
        <button onClick={onClick} className={`bg-blue-300 ${props.className?props.className : ""}`}>
            {children}
        </button>
    </>
}