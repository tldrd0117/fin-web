import React from 'react';
import { Link } from 'react-router-dom';

export default (props) => {
    const { data } = props;
    return <>
        <style jsx>{`
            .breadcrumb .breadcrumb-item {
                position: relative;
            }
            .breadcrumb .breadcrumb-item:first-child {
                margin-left: 0 !important;
            }
            .breadcrumb .breadcrumb-item:not(:last-child):after {
                content: '/';
            }
        `}</style>
        <nav aria-label="breadcrumb"> 
            <ol className="breadcrumb flex">
            {
                data.map((v,i)=>{
                    if(i==data.length-1){
                        <li key={v.name} className="breadcrumb-item active text-purple-700 hover:text-purple-700 mx-2" aria-current="page">{v.name}</li> 
                    }
                    return <li key={v.name} className="breadcrumb-item text-gray-600"><Link to={v.link || ""} className="text-gray-600 hover:text-purple-700 mx-2">{v.name}</Link></li>
                })
            }
            </ol>
        </nav>
    </>
}