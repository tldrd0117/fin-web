import React from 'react';
import AppBar from '../containers/AppBar';
import CrawlingBoard from '../containers/CrawlingBoard';
import Menu from '../containers/Menu';

export default () => {
    return <>
    
        <style jsx global>{`
            .appbar{
                height: 60px;
            }
            .menu-layout{
                @apply flex flex-row h-full;
            }
            .top-down-layout{
                @apply flex flex-col h-full;
            }
        `}</style>
        <div className={"top-down-layout"}>
            <AppBar className={"w-full appbar"} title={"Fin Crawling App"}>
            </AppBar>
            <div className={"menu-layout"}>
                <Menu menus={["일자별 주식 및 시가총액"]}/>
                <CrawlingBoard/>
            </div>
        </div>
    </>
}