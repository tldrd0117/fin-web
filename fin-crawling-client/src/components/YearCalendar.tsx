import React, { useState, CSSProperties, useEffect, useCallback, useRef } from 'react';
import format from 'date-fns/format';
import parseISO from 'date-fns/parseISO';
import getYear from 'date-fns/getYear';
import { ColorInput } from 'tinycolor2';
import { GridLoader } from 'react-spinners';



import * as styles from '../styles/calendar.css';

import {
  DEFAULT_THEME,
  LINE_HEIGHT,
  MIN_DISTANCE_MONTH_LABELS,
  NAMESPACE,
  Theme,
  ApiResult,
  createCalendarTheme, getClassName,
  GraphData, Block, getGraphData, updateGraphData
} from '../utils/CalendarUtils';
import { useSelector } from 'react-redux';
import { RootState } from '../data/root/rootReducer';
import ReactTooltip from 'react-tooltip';
import SequentialList from 'react-sequential-list';
import useStateCallback from '../utils/hook/useStateCallback';


export function usePrevious<T>(value: T): T {
    const ref = useRef<T>(value);

    useEffect(() => {
        ref.current = value;
    }, [value]);

    return ref.current;
}

export type Props = {
  username?: string;
  blockMargin?: number;
  blockSize?: number;
  color?: ColorInput;
  dateFormat?: string;
  fontSize?: number;
  fullYear?: boolean;
  showTotalCount?: boolean;
  style?: CSSProperties;
  theme?: Theme;
  market?: string;
  years?: Array<number>;
  task?: ApiResult
};

const YearCalendar: React.FC<Props> = ({
  username,
  blockMargin = 2,
  blockSize = 12,
  children,
  color = undefined,
  dateFormat = 'MMM d, yyyy',
  fontSize = 14,
  fullYear = true,
  showTotalCount = true,
  style = {},
  market = "kospi",
  theme = undefined,
  years = [Number(format(new Date(), 'yyyy'))],
  task = { years:{}, stocks:[], lastUpdateYear: 2021}
}) => {
  const [graphs, setGraphs] = useStateCallback<Array<GraphData> | null>([]);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setLoading] = useState(true)

  const prevYears = usePrevious(years);
  const prevUsername = usePrevious(username);
  const prevFullYear = usePrevious(fullYear);

  // useEffect(() => {
    // console.log("changeGraphs", graphs.length)
    // ReactTooltip.rebuild()
  // },[graphs])

  const fetchData = useCallback(() => {
    setError(null);
    if(graphs.length > 0){
      console.log("updateGraphData")
      setLoading(true);
      updateGraphData(task, {years, lastYear: fullYear}, graphs)
      .then(setGraphs)
      .catch(setError)
    } else {
      console.log("getGraphData")
      console.log(task)
      const now = Date.now();
      getGraphData(task,{
        years,
        lastYear: fullYear,
      })
        .then(setGraphs)
        .then(() => {
          console.log("getGraphDataTimes:"+(Date.now() - now))
        })
        .catch(setError);
    }
  }, [task.lastUpdateYear]);
  // Refetch if relevant props change
  useEffect(() => {
      console.log("fetchData")
      fetchData();
  }, [task.lastUpdateYear]);

  function getTheme(): Theme {
    if (theme) {
      return Object.assign({}, DEFAULT_THEME, theme);
    }

    if (color) {
      return createCalendarTheme(color);
    }

    return DEFAULT_THEME;
  }

  function getDimensions() {
    const textHeight = Math.round(fontSize * LINE_HEIGHT);

    // Since weeks start on Sunday, there is a good chance that the graph starts
    // in the week before January 1st. Therefore, the calendar shows 53 weeks.
    const width = (52 + 1) * (blockSize + blockMargin) - blockMargin;
    const height = textHeight + (blockSize + blockMargin) * 7 - blockMargin;

    return { width, height };
  }

  function getTooltipMessage(day: Required<Block>) {
    const date = parseISO(day.date);
    
    return `<strong>${day.info.level == 2? "성공" : 
                    day.info.level == 3? "실패" : "대기" }</strong> ${date.getFullYear()}년 ${date.getMonth()+1}월 ${date.getDate()}일`;
  }

  function renderMonthLabels(monthLabels: GraphData['monthLabels']) {
    const style = {
      fill: getTheme().text,
      fontSize,
    };

    const now = Date.now();
    useEffect(() => {
      console.log("renderMonthLabelsTimes:"+(Date.now() - now))
    },[])

    // Remove the first month label if there's not enough space to the next one
    // (end of previous month)
    if (monthLabels[1].x - monthLabels[0].x <= MIN_DISTANCE_MONTH_LABELS) {
      monthLabels.shift();
    }

    return monthLabels.map(month => (
      <text x={(blockSize + blockMargin) * month.x} y={fontSize} key={month.x} style={style}>
        {month.label}
      </text>
    ));
  }

  const Block = (day: Block&{y}) => {
    const theme = getTheme();
    const textHeight = Math.round(fontSize * LINE_HEIGHT);
    return <rect
      x="0"
      y={textHeight + (blockSize + blockMargin) * day.y}
      width={blockSize}
      height={blockSize}
      fill={theme[`grade${day.info ? day.info.level : 0}`]}
      data-tip={day.info ? getTooltipMessage(day as Required<Block>) : null}
      key={`${day.date}-${day.info?day.info.count:""}-${day.info?day.info.level:""}`}
    />
  }

  const Blocks = React.memo((props: {blocks}) => {
    const blocks: GraphData['blocks'] = props.blocks;
    const now = Date.now();
    useEffect(() => {
      console.log("renderBlocksTimes:"+(Date.now() - now))
    },[])
    return <>
      {
        blocks
        .map(week =>
          week.map((day, y) => {
            return <Block date={day.date} info={day.info} y={y}/>
          }),
        )
        .map((week, x) => {
          return (
          <g key={x} transform={`translate(${(blockSize + blockMargin) * x}, 0)`}>
            {week}
          </g>
        )}
        )
      }
      </>
  }, (prev, next) => {
    const prevBlocks = prev.blocks;
    const nextBlocks = next.blocks;
    if(prevBlocks.length != nextBlocks.length){
      return false;
    }
    for(let i = 0; i < prevBlocks.length; ++i){
      if(prevBlocks[i].length != nextBlocks[i].length){
        return false;
      }
      for(let j = 0; j < prevBlocks[i].length; ++j){
        if(prevBlocks[i][j].date!=nextBlocks[i][j].date || prevBlocks[i][j].info.level!=nextBlocks[i][j].info.level){
          return false;
        }
      }
    }
    return true;
  })

  function renderTotalCount(year: number, totalCount: number) {
    const isCurrentYear = getYear(new Date()) === year;

    return (
      <div className={getClassName('meta')} style={{ fontSize }}>
        {isCurrentYear && fullYear ? 'Last year' : year}
        {' – '}
        {isCurrentYear && !fullYear ? '총 ' : null}
        {totalCount} 일
      </div>
    );
  }

  const { width, height } = getDimensions();

  if (error) {
    console.error(error);
    return <p>Error :(</p>;
  }

  // if (isLoading) {
  //   return <div className={"flex"}>
  //       <GridLoader color={"#ebedf0"} size={15} margin={2} loading={true} />
  //       <GridLoader color={"#22C55E"} size={15} margin={2} loading={true} />
  //       <GridLoader color={"#f87171"} size={15} margin={2} loading={true} />
  //     </div>
  //   // return <div className={getClassName('loading', styles.loading)}>Loading …</div>;
  // }

  // const ListGraphsItems = ({graph}) => {
  const ListGraphsItems = ({graph, onComplete = null, isLast}) => {
    const { year, blocks, monthLabels, totalCount } = graph;
    const now = Date.now();
    useEffect(() => {
      if(onComplete) {
        console.log(market+" onComplete: "+ year)
        if(isLast){
          setLoading(false)
        }
        onComplete();
      }
      console.log("graphsItemTimes:"+(Date.now()-now));
    },[onComplete])
    return (
      <div key={year} className={getClassName('chart', styles.chart)}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
          className={"calendar"}
          style={{ backgroundColor: theme?.background }}
        >
          {renderMonthLabels(monthLabels)}
          <Blocks blocks={blocks}/>
        </svg>

        {showTotalCount && renderTotalCount(year, totalCount)}
        {children}
      </div>
    );
  }

  return (
    <article className={NAMESPACE} style={style}>
      <SequentialList>
        {graphs.map((graph, i) => {
          return <ListGraphsItems graph={graph} isLast={i==graphs.length-1}/>
        })}
      </SequentialList>
      {
        isLoading?<div className={"flex"}>
          <GridLoader color={"#ebedf0"} size={10} margin={2} loading={true} />
          <GridLoader color={"#22C55E"} size={10} margin={2} loading={true} />
          <GridLoader color={"#f87171"} size={10} margin={2} loading={true} />
        </div>:null
      }
    </article>
  );
};

export default YearCalendar;