import React from 'react';

export default (props) => {
    return <>
        <style jsx>{`
            span{
                padding: 10px 0px 10px 20px;
                &:hover{
                    @apply bg-gray-900;
                }
            }
        `}</style>
        <span className={"text-white"}>{props.children}</span>
    </>
}
