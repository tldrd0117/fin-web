import React, { useEffect } from 'react'
import { useSelector } from 'react-redux';
import YearCalendar from '../components/YearCalendar';
import { RootState } from '../data/root/rootReducer';
import ReactTooltip from 'react-tooltip';
import SequentialList from 'react-sequential-list';

const ListItem = ({task, market, onComplete = null}) => {
    useEffect(() => {
        if (onComplete) {
          onComplete();
        }
    },[onComplete])

    return <div className={"mt-4"}>
        <p className={"mt-4 mb-2"}>{market}</p>
        <YearCalendar
            blockSize={10} blockMargin={4}
            fullYear={false}
            style={{maxWidth:"100%"}}
            task={task.yearData["marcap"][market]}
            years={task.yearData["marcap"][market].yearArray}
        >
            <ReactTooltip delayShow={50} html />
    </YearCalendar>
</div>
}

export default (props) =>{
    const task = useSelector((state: RootState) => state.task)
    return <SequentialList>
        {
            Object.keys(task.calendar.data["marcap"]).map(market=>{
                return <ListItem task={task} market={market}/>
            })
        }
    </SequentialList>
};