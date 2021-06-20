import React from 'react';
import MenuItem from '../components/MenuItem';

export default (props) => {
    const { menus } = props;
    return <>
        <style jsx>{`
            .menu{
                width: 300px;
                height: 100%;
                overflow: auto;
                padding-top: 20px;
            }
        `}</style>
        <div className={"menu shadow bg-gray-700 flex flex-col"}>
            {menus.map(v=><MenuItem key={v}>{v}</MenuItem>)}
        </div>
    </>
}
