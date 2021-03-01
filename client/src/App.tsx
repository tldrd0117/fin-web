import React from 'react';
import LoginButton from './components/LoginButton';

export default () => {
    const hello : string = "HELLO2";
    return <>
        <label>{hello}</label>
        <LoginButton/>
    </>
}