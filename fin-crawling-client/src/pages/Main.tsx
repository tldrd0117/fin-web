import React, { Component, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import AppBar from '../containers/AppBar';
import CrawlingBoard from '../containers/CrawlingBoard';
import Menu from '../containers/Menu';
import { RootState } from '../data/root/rootReducer'
import { endConnection, startConnection } from '../data/socket/socketSlice';
import { menus } from '../constants/Menu'
import { fetchPublicKey } from '../data/user/userSlice';

export default ( {SubComponent = null}) => {
    const { isConnected } = useSelector((state: RootState)=>state.socket)
    const dispatch = useDispatch()
    useEffect(() => {
        dispatch(startConnection({}))
        return function unmont() {
            dispatch(endConnection({}))
        }
    },[])
    const [isMenuOpen, setMenuOpen] = useState(false)
    return <>
        <style jsx global>{`
            .appbar{
                height: 60px;
                @apply flex-none;
                @apply absolute;
                @apply z-50;
                background: white;
            }
            .menu-layout{
                height: calc(100% - 60px);
                margin-top: 60px;
                @apply flex flex-row flex-grow fixed;
            }
            .content-layout{
                margin-top: 60px;
                height: calc(100% - 60px);
                @apply flex flex-row flex-grow;
            }
            .top-down-layout{
                @apply flex flex-col h-full;
                @apply overflow-auto;
            }
            .connect{
                font-family: 'LAB디지털';
                @apply absolute right-2;
            }
            .menu-layout-2{
                margin-top: 60px;
            }

            @font-face {
                font-family: 'LAB디지털';
                src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_20-07@1.0/LAB디지털.woff') format('woff');
                font-weight: normal;
                font-style: normal;
            }
        `}</style>
        <div className={"top-down-layout"}>
            <AppBar
                onMenuIconClick={()=>setMenuOpen(!isMenuOpen)}
                className={"w-full appbar"} 
                title={"스크래핑을 위한 스크래핑"}>
                {
                    isConnected?<div className={"connect text-green-500"}>연결</div>:
                    <div className={"connect text-red-500"}>연결끊김</div>
                }
                
            </AppBar>
            
            <div className={"w-full ml-0 sm:ml-[250px] sm:w-[calc(100%_-_250px)]"}>
                 {SubComponent? <SubComponent/>:null}
            </div>

            <div className={"menu-layout w-[250px]"}>
                <Menu className={"hidden sm:block"} menus={menus}/>
            </div>
            {
                isMenuOpen?<div className={"sm:hidden fixed z-50 w-full h-full menu-layout-2"}>
                    <Menu onClick={()=>setMenuOpen(!isMenuOpen)} menus={menus}/>
                </div>:null
            }
        </div>
    </>
}