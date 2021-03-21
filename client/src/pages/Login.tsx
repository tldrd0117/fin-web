import React from 'react';
import LoginBox from '../containers/LoginBox';

export default () => {
    return <>
        <div
            className={"absolute w-full h-full flex flex-col items-center justify-center"}
            >
            <LoginBox/>
        </div>
        
    </>
}