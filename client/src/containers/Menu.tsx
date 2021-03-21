import React from 'react';
import MenuItem from '../components/MenuItem';

export default (props) => {
    const { menus } = props;
    return <>
        <style jsx>{`
            .menu{
                width: 224px;
                height: 100%;
                overflow: auto;
                padding-top: 20px;
            }
        `}</style>
        <div className={"menu shadow bg-gray-700 flex flex-col"}>
            {menus.map(v=><MenuItem>{v}</MenuItem>)}
        </div>
    </>
}
