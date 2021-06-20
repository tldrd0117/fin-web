import React from 'react'
import { useSelector } from 'react-redux';
import Card from '../components/Card';
import { RootState } from '../data/root/rootReducer';
import CrawlingCompleteList from './CrawlingCompleteList';
import CrawlingForm from './CrawlingForm';
import CrawlingProgressList from './CrawlingProgressList';


export default (props) =>{
    
    return <Card className={"mt-10 relative"}>
            <CrawlingForm/>
            <div className={"w-full h-px bg-gray-300 mt-8 mb-4"}></div>
            <p>Progress List</p>
            <CrawlingProgressList taskId={"marcap"}/>
            <p className={"mt-2"}>Completed History</p>
            <CrawlingCompleteList taskId={"marcap"}/>
        </Card>

}