import React, { Component, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import AppBar from '../containers/AppBar';
import CrawlingBoard from '../containers/CrawlingBoard';
import Menu from '../containers/Menu';
import { RootState } from '../data/root/rootReducer'
import { endConnection, startConnection } from '../data/socket/socketSlice';

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
                margin-top: 60px;
                @apply flex flex-row flex-grow;
            }
            .top-down-layout{
                @apply flex flex-col h-full;
                @apply overflow-auto;
            }
            .connect{
                @apply absolute right-2;
            }
            .menu-layout-2{
                margin-top: 60px;
            }
        `}</style>
        <div className={"top-down-layout"}>
            <AppBar
                onMenuIconClick={()=>setMenuOpen(!isMenuOpen)}
                className={"w-full appbar"} 
                title={"Fin Crawling App"}>
                {
                    isConnected?<div className={"connect text-green-500"}>연결</div>:
                    <div className={"connect text-red-500"}>연결끊김</div>
                }
                
            </AppBar>
            <div className={"menu-layout"}>
                <Menu className={"hidden sm:block"} menus={["일자별 주식 및 시가총액"]}/>
                 {SubComponent? <SubComponent/>:null}
            </div>
            {
                isMenuOpen?<div className={"sm:hidden fixed z-50 w-full h-full menu-layout-2"}>
                    <Menu onClick={()=>setMenuOpen(!isMenuOpen)} menus={["일자별 주식 및 시가총액"]}/>
                </div>:null
            }
            

        </div>
    </>
}