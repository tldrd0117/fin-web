import _ from 'lodash'

export const getDateString = (date: Date) => {
    return [
            date.getFullYear(),
            _.padStart((date.getMonth() + 1).toString(),2,"0"),
            _.padStart(date.getDate().toString(),2,"0")].join("")
}

export const getDateHipen = (str: string) => {
    if(str && str.length){
        return [str.slice(0,4),str.slice(4,6),str.slice(6,8)].join("-");
    }
    return "";
}