import React, {useState} from 'react';
import YearCalendar from '../components/YearCalendar';
import ReactTooltip from 'react-tooltip';

export default ({yearData, count = 3}) => {
    const [yearCalandarPage, setYearCalandarPage] = useState(1);

    const handleNext = () => {
        setYearCalandarPage(yearCalandarPage + 1);
        console.log(count * yearCalandarPage, yearData["marcap"]["kospi"].yearArray.length)
    }

    return <>
    {
        Object.keys(yearData["marcap"]).map(market=>{
            return <div className={"mt-4"}>
                <p className={"mt-4 mb-2"}>{market}</p>
                <YearCalendar
                    key={market}
                    blockSize={10} blockMargin={4}
                    fullYear={false}
                    market={market}
                    style={{maxWidth:"100%"}}
                    task={yearData["marcap"][market]}
                    years={yearData["marcap"][market].yearArray.slice(0, yearCalandarPage*count)}
                >
                    <ReactTooltip delayShow={50} html />
                </YearCalendar>
                {
                    count * yearCalandarPage < yearData["marcap"][market].yearArray.length?
                    <td onClick={handleNext} className={"text-center text-sm p-4 cursor-pointer"} colSpan={6}>더보기</td>:
                    null
                }
                
            </div>
            
        })}
    </>
}