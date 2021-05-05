import _ from 'lodash'

export const getDateString = (date: Date) => {
    return [
            date.getFullYear(),
            _.padStart((date.getMonth() + 1).toString(),2,"0"),
            _.padStart(date.getDate().toString(),2,"0")].join("")
}