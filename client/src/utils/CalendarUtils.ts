export type Theme = {
    [key: string]: string;
    background: string;
    text: string;
    grade4: string;
    grade3: string;
    grade2: string;
    grade1: string;
    grade0: string;
  };
  
  export const DEFAULT_THEME = {
    background: 'transparent',
    text: '#000',
    grade4: '#216e39',
    grade3: '#30a14e',
    grade2: '#34d399',
    grade1: '#f87171',
    grade0: '#ebedf0',
  };
  
  export const NAMESPACE = 'react-github-calendar';
  
  export const LINE_HEIGHT = 1.5;
  export const MIN_DISTANCE_MONTH_LABELS = 2;

  import color, { ColorInput } from 'tinycolor2';


export function createCalendarTheme(
  baseColor: ColorInput,
  textColor = 'inherit',
  emptyCellColor = color('white').darken(8).toHslString(),
  background = 'transparent',
): Theme {
  const base = color(baseColor);

  if (!base.isValid()) {
    return DEFAULT_THEME;
  }

  const text = color(textColor).isValid() ? String(color(textColor)) : DEFAULT_THEME.text;

  return {
    background,
    text,
    grade4: base.setAlpha(0.92).toHslString(),
    grade3: base.setAlpha(0.76).toHslString(),
    grade2: base.setAlpha(0.6).toHslString(),
    grade1: base.setAlpha(0.44).toHslString(),
    grade0: emptyCellColor,
  };
}

export function getClassName(name: string, extra?: string): string {
  if (extra) {
    return `${NAMESPACE}__${name} ${extra}`;
  }

  return `${NAMESPACE}__${name}`;
}

// Import modules separately to reduce bundle size
import addDays from 'date-fns/addDays';
import format from 'date-fns/format';
import getDay from 'date-fns/getDay';
import getMonth from 'date-fns/getMonth';
import isAfter from 'date-fns/isAfter';
import isSameYear from 'date-fns/isSameYear';
import parseISO from 'date-fns/parseISO';
import setDay from 'date-fns/setDay';
import subYears from 'date-fns/subYears';

const API_URL = 'https://ancient-butterfly.herokuapp.com/v3/';
const DATE_FORMAT = 'yyyyMMdd';

export type Block = {
  date: string;
  info?: {
    date: string;
    count: number;
    level: number;
  };
};

interface MonthLabel {
  x: number;
  label: string;
}

export interface GraphData {
  year: number;
  blocks: Array<Array<Block>>;
  monthLabels: Array<MonthLabel>;
  totalCount: number;
}

export interface RequestOptions {
  years: Array<number>;
  lastYear: boolean;
}

export interface ApiResult {
  years: {
    [year: number]: number;
    [year: string]: number; // lastYear
  };
  stocks: Array<{
    date: string;
    count: number;
    level: number;
  }>;
}

function getContributionsForDate(data: ApiResult, date: string) {
  return data.stocks.find(contrib => contrib.date === date);
}

function getBlocksForYear(year: number, data: ApiResult, lastYear: boolean) {
  const now = new Date();
  const firstDate = lastYear ? subYears(now, 1) : parseISO(`${year}-01-01`);
  const lastDate = lastYear ? now : parseISO(`${year}-12-31`);

  let weekStart = firstDate;

  // The week starts on Sunday - add days to get to next sunday if neccessary
  if (getDay(firstDate) !== 0) {
    weekStart = addDays(firstDate, getDay(firstDate));
  }

  // Fetch graph data for first row (Sundays)
  const firstRowDates = [];
  while (weekStart <= lastDate) {
    const date = format(weekStart, DATE_FORMAT);

    firstRowDates.push({
      date,
      info: getContributionsForDate(data, date),
    });

    weekStart = setDay(weekStart, 7);
  }

  // Add the remainig days per week (column for column)
  return firstRowDates.map(dateObj => {
    const dates = [];
    for (let i = 0; i <= 6; i += 1) {
      const date = format(setDay(parseISO(dateObj.date), i), DATE_FORMAT);

      if (isAfter(parseISO(date), lastDate)) {
        break;
      }

      dates.push({
        date,
        info: getContributionsForDate(data, date),
      });
    }

    return dates;
  });
}

function getMonthLabels(blocks: GraphData['blocks'], lastYear: boolean): Array<MonthLabel> {
  const weeks = blocks.slice(0, lastYear ? blocks.length - 1 : blocks.length);
  let previousMonth = 0; // January

  return weeks.reduce<Array<MonthLabel>>((labels, week, x) => {
    const firstWeekDay = parseISO(week[0].date);
    const month = getMonth(firstWeekDay) + 1;
    const monthChanged = month !== previousMonth;
    const firstMonthIsDecember = x === 0 && month === 12;

    if (monthChanged && !firstMonthIsDecember) {
      labels.push({
        x,
        label: format(firstWeekDay, 'MMM'),
      });
      previousMonth = month;
    }

    return labels;
  }, []);
}

function getGraphDataForYear(year: number, data: ApiResult, lastYear: boolean): GraphData {
  console.log(data)
  const blocks = getBlocksForYear(year, data, lastYear);
  const monthLabels = getMonthLabels(blocks, lastYear);
  const totalCount = data.years[lastYear ? 'lastYear' : year] ?? 0;
  console.log(year, blocks, monthLabels, totalCount)
  return {
    year,
    blocks,
    monthLabels,
    totalCount,
  };
}

export async function getGraphData(data: ApiResult, options: RequestOptions): Promise<Array<GraphData>> {
  const { years, lastYear } = options;
  // const data: ApiResult = await (await fetch(`${API_URL}${username}?y=all&y=lastYear`)).json();
  console.log(data)
  if (!Object.keys(data.years).length) {
    throw Error('No data available');
  }

  return years.map(year => {
    const isCurrentYear = isSameYear(parseISO(String(year)), new Date());
    console.log(year)
    return getGraphDataForYear(year, data, isCurrentYear && lastYear);
  });
}